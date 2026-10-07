"""
RG-12 traceability workbook sync.

Keeps the "RG-12. Trazabilidad del Servicio" Excel stored in Nextcloud up to date:
one row per (offer, service). The workbook is edited at XML level (only the
PRESTACIÓN sheet and its table) so dropdowns, pivot tables and images in the
original file are preserved, which openpyxl would otherwise drop.
"""
import io
import logging
import os
import re
import threading
import warnings
import zipfile
from datetime import date, datetime

import openpyxl
from lxml import etree

from backend import models, workflow
from backend.nextcloud import get_nextcloud_client

logger = logging.getLogger(__name__)

QUALITY_REMOTE_ROOT = os.getenv("NEXTCLOUD_QUALITY_PATH", "/SGO-test").rstrip("/")
TRACEABILITY_FILE = os.getenv("NEXTCLOUD_TRACEABILITY_FILE")  # optional explicit file name
SHEET_PATH = "xl/worksheets/sheet1.xml"
FIRST_DATA_ROW = 8
COLUMNS = "ABCDEFGHIJKLMNOPQR"
DATE_COLUMNS = {"G", "H", "K", "M"}
DEFAULT_STYLES = {"G": "15", "H": "15", "K": "15", "M": "15", "N": "16"}
MAIN_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"m": MAIN_NS}
_lock = threading.Lock()

CLIENT_TYPES = {
    "internal": "INTERNO",
    "mina": "INTERNO",
    "csic": "EXTERNO_CSIC",
    "uam": "EXTERNO_UAM",
    "university": "EXTERNO_OPI/UNIVERSIDAD",
    "universidad": "EXTERNO_OPI/UNIVERSIDAD",
    "opis": "EXTERNO_OPI/UNIVERSIDAD",
    "company": "EXTERNO_COMPAÑÍA PRIVADA",
    "empresa": "EXTERNO_COMPAÑÍA PRIVADA",
}


def _q(tag: str) -> str:
    return f"{{{MAIN_NS}}}{tag}"


def _fmt_date(value) -> str:
    return value.strftime("%d/%m/%Y") if value else ""


def _service_rows(db, offer) -> list[dict]:
    """Build the RG-12 values for every active service of an offer."""
    client = offer.client
    is_internal = bool(client) and client.entity.lower() in ("internal", "mina")
    rows = []
    for service in workflow.active_services(offer):
        entry = db.query(models.TraceabilityEntry).filter(
            models.TraceabilityEntry.service_id == service.id
        ).first()
        technician = service.technician
        mina = entry.mina_autoservicio if entry and entry.mina_autoservicio else (
            f"MiNa ({technician.first_name} {technician.last_name})" if technician else None
        )
        hours = service.hours if service.hours else None
        rows.append({
            "A": offer.reference,
            "B": f"{client.first_name} {client.last_name}".strip() if client else None,
            "C": CLIENT_TYPES.get(client.entity.lower()) if client else None,
            "D": client.grupo if is_internal else None,
            "E": offer.cuenta_interna,
            "F": offer.codigo_proyecto,
            "G": (entry.request_date if entry and entry.request_date else offer.created_at),
            "H": entry.acceptance_date if entry else None,
            "I": mina,
            "J": entry.sample_provided if entry else None,
            "K": entry.verification if entry else None,
            "L": service.service_name,
            "M": (entry.delivery_date if entry and entry.delivery_date else offer.delivery_date),
            "N": service.quoted_price,
            "O": hours,
            "P": entry.charge_note if entry else None,
            "Q": entry.conformity if entry else None,
            "R": entry.observations if entry else None,
        })
    return rows


def _find_workbook_name(client, year: int) -> str | None:
    if TRACEABILITY_FILE:
        return TRACEABILITY_FILE
    names = client.list_names(QUALITY_REMOTE_ROOT) or set()
    candidates = sorted(
        n for n in names
        if n.startswith("RG-12") and n.endswith(".xlsx") and str(year) in n
    )
    return candidates[-1] if candidates else None


def _existing_rows(xlsx_bytes: bytes) -> tuple[dict, int]:
    """Map (code, service) -> row number, and return the first empty data row."""
    with warnings.catch_warnings():
        # Read-only use: the workbook is never saved through openpyxl, so the
        # "Data Validation extension" warning is harmless.
        warnings.filterwarnings("ignore", message="Data Validation extension")
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), read_only=True, data_only=True)
    ws = wb.worksheets[0]
    index, next_row = {}, FIRST_DATA_ROW
    for number, values in enumerate(
        ws.iter_rows(min_row=FIRST_DATA_ROW, max_col=12, values_only=True), start=FIRST_DATA_ROW
    ):
        code, service = values[0], values[11]
        if code:
            next_row = number + 1
            index.setdefault(str(code).strip(), []).append((number, str(service or "").strip()))
    wb.close()
    return index, next_row


def _column_index(ref: str) -> int:
    return COLUMNS.index(re.match(r"[A-Z]+", ref).group(0))


def _get_row(sheet_data, number: int, template_row=None):
    rows = sheet_data.findall("m:row", NS)
    for row in rows:
        if int(row.get("r")) == number:
            return row
    new_row = etree.SubElement(sheet_data, _q("row"), r=str(number), spans="1:18")
    # Keep rows ordered
    sheet_data.remove(new_row)
    position = sum(1 for row in rows if int(row.get("r")) < number)
    sheet_data.insert(position, new_row)
    return new_row


def _get_cell(row, column: str):
    ref = f"{column}{row.get('r')}"
    cells = row.findall("m:c", NS)
    for cell in cells:
        if cell.get("r") == ref:
            return cell
    cell = etree.Element(_q("c"), r=ref)
    if column in DEFAULT_STYLES:
        cell.set("s", DEFAULT_STYLES[column])
    else:
        cell.set("s", "10")
    position = sum(1 for c in cells if _column_index(c.get("r")) < COLUMNS.index(column))
    row.insert(position, cell)
    return cell


def _set_cell(row, column: str, value):
    cell = _get_cell(row, column)
    for child in list(cell):
        cell.remove(child)
    cell.attrib.pop("t", None)
    if isinstance(value, (datetime, date)):
        base = datetime(1899, 12, 30)
        moment = value if isinstance(value, datetime) else datetime(value.year, value.month, value.day)
        etree.SubElement(cell, _q("v")).text = str((moment - base).days)
    elif isinstance(value, (int, float)):
        etree.SubElement(cell, _q("v")).text = repr(float(value)) if isinstance(value, float) else str(value)
    else:
        cell.set("t", "inlineStr")
        inline = etree.SubElement(cell, _q("is"))
        text = etree.SubElement(inline, _q("t"))
        text.text = str(value)
        text.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")


def _extend_capacity(sheet_root, table_root, last_row: int):
    """Add pre-styled empty rows (copy of the last row) so the table has room for last_row."""
    sheet_data = sheet_root.find("m:sheetData", NS)
    rows = sheet_data.findall("m:row", NS)
    current_last = int(rows[-1].get("r"))
    if last_row <= current_last:
        return
    for number in range(current_last + 1, last_row + 1):
        copy = etree.fromstring(etree.tostring(rows[-1]))
        copy.set("r", str(number))
        for cell in copy.findall("m:c", NS):
            cell.set("r", f"{re.match(r'[A-Z]+', cell.get('r')).group(0)}{number}")
            for child in list(cell):
                cell.remove(child)
            cell.attrib.pop("t", None)
        sheet_data.append(copy)
    sheet_root.find("m:dimension", NS).set("ref", f"A1:R{last_row}")
    for element in table_root.iter():
        if element.tag in (_q("table"), _q("autoFilter")) and element.get("ref"):
            element.set("ref", re.sub(r"\d+$", str(last_row), element.get("ref")))


def _update_workbook(xlsx_bytes: bytes, offer_rows: list[dict]) -> bytes:
    index, next_row = _existing_rows(xlsx_bytes)
    code = offer_rows[0]["A"]
    known = list(index.get(code, []))

    placements = []
    for data in offer_rows:
        match = next((item for item in known if item[1] == data["L"]), None)
        if not match:
            match = next((item for item in known if not item[1]), None)
        if match:
            known.remove(match)
            placements.append((match[0], data))
        else:
            placements.append((next_row, data))
            next_row += 1

    with zipfile.ZipFile(io.BytesIO(xlsx_bytes)) as source:
        sheet_root = etree.fromstring(source.read(SHEET_PATH))
        table_name = next(
            n for n in source.namelist()
            if n.startswith("xl/tables/") and b'displayName="Tabla1"' in source.read(n)
        )
        table_root = etree.fromstring(source.read(table_name))
        _extend_capacity(sheet_root, table_root, max(number for number, _ in placements))

        sheet_data = sheet_root.find("m:sheetData", NS)
        for number, data in placements:
            row = _get_row(sheet_data, number)
            for column, value in data.items():
                if value not in (None, ""):
                    _set_cell(row, column, value)

        # Extend dropdown validations (x14) to cover the table.
        xml_text = etree.tostring(sheet_root, xml_declaration=True, encoding="UTF-8", standalone=True).decode("utf-8")
        last = max(number for number, _ in placements)
        xml_text = re.sub(
            r"<xm:sqref>([A-Z])8:\1(\d+)</xm:sqref>",
            lambda m: f"<xm:sqref>{m.group(1)}8:{m.group(1)}{max(int(m.group(2)), last, 336)}</xm:sqref>",
            xml_text,
        )

        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                content = source.read(item.filename)
                if item.filename == SHEET_PATH:
                    content = xml_text.encode("utf-8")
                elif item.filename == table_name:
                    content = etree.tostring(table_root, xml_declaration=True, encoding="UTF-8", standalone=True)
                elif item.filename.startswith("xl/pivotCache/pivotCacheDefinition") and item.filename.endswith(".xml"):
                    if b"refreshOnLoad" not in content:
                        content = content.replace(b"<pivotCacheDefinition ", b'<pivotCacheDefinition refreshOnLoad="1" ', 1)
                target.writestr(item, content)
        return output.getvalue()


def sync_offer(db, offer) -> bool:
    """Create or update the RG-12 rows (one per active service) of an offer."""
    if not (os.getenv("NEXTCLOUD_USERNAME") and os.getenv("NEXTCLOUD_PASSWORD")):
        return False
    offer_rows = _service_rows(db, offer)
    if not offer_rows or not offer.reference:
        return False
    return _push_rows(offer_rows, (offer.created_at or datetime.now()).year)


def _push_rows(offer_rows: list[dict], year: int) -> bool:
    client = get_nextcloud_client()
    file_name = _find_workbook_name(client, year)
    if not file_name:
        logger.warning("RG-12 workbook for %s not found in %s", year, QUALITY_REMOTE_ROOT)
        return False
    remote = f"{QUALITY_REMOTE_ROOT}/{file_name}"

    with _lock:
        response = client.session.get(client._build_url(remote))
        if response.status_code != 200:
            raise RuntimeError(f"Could not download {remote}: {response.status_code}")
        updated = _update_workbook(response.content, offer_rows)
        put = client.session.put(client._build_url(remote), data=updated)
        if put.status_code not in (200, 201, 204):
            raise RuntimeError(f"Could not upload {remote}: {put.status_code}")
    return True


def try_sync_offer_background(db, offer) -> None:
    """Read the offer data now, then upload to the workbook in a background thread."""
    try:
        if not (os.getenv("NEXTCLOUD_USERNAME") and os.getenv("NEXTCLOUD_PASSWORD")):
            return
        offer_rows = _service_rows(db, offer)
        if not offer_rows or not offer.reference:
            return
        year = (offer.created_at or datetime.now()).year
    except Exception:
        logger.exception("RG-12 traceability sync failed for offer %s", getattr(offer, "reference", None))
        return

    def run():
        try:
            _push_rows(offer_rows, year)
        except Exception:
            logger.exception("RG-12 traceability sync failed for offer %s", offer_rows[0].get("code"))

    threading.Thread(target=run, daemon=True).start()


def try_sync_offer(db, offer) -> None:
    """Best-effort sync: a spreadsheet problem must never break the offer workflow."""
    try:
        sync_offer(db, offer)
    except Exception:
        logger.exception("RG-12 traceability sync failed for offer %s", getattr(offer, "reference", None))
