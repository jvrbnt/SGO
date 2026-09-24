import hashlib
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from docx import Document
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from sqlalchemy import select, text

from backend import models, workflow

"""
PDF Document Generation Module
This module uses the 'reportlab' library to natively generate immutable PDF 
documents for Offers and Invoices. Generating PDFs directly via code is highly 
efficient for the server and avoids the need for heavy external dependencies 
like LibreOffice or Microsoft Word.
"""

# Directory where all generated PDFs will be stored persistently.
DOCUMENT_ROOT = Path(os.getenv("GENERATED_DOCUMENTS_DIR", "data/generated_documents"))
PO_REQUEST_DIRECTORY = Path(os.getenv("PO_REQUEST_DIRECTORY", "Calidad/Mail Petición Oferta"))
ACCEPTANCE_DOCUMENT_DIRECTORY = Path(os.getenv("ACCEPTANCE_DOCUMENT_DIRECTORY", "Calidad/Mail Aceptación Oferta"))
OFFER_DOCUMENT_DIRECTORY = Path(os.getenv("OFFER_DOCUMENT_DIRECTORY", "Calidad/RG-10. Ofertas. Ed 03"))
INVOICE_DOCUMENT_DIRECTORY = Path(os.getenv("INVOICE_DOCUMENT_DIRECTORY", "Calidad/Facturas"))
RG10_TEMPLATE_PATH = Path(os.getenv("RG10_TEMPLATE_PATH", "docs_oficiales/CSS_RG-10. Oferta Ed.05_ES.docx"))
PO_REQUEST_FILENAME = re.compile(
    r"^PO_(?P<number>\d+)_(?P<year>\d{4})(?:_Actualizada(?:_\d+)?)?\.pdf$"
)


def _safe_part(value) -> str:
    text = str(value or "").strip()
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text)
    return text.strip("._") or "document"


def _quality_document_path(year: int, folder: str, stem: str, extension: str = "pdf") -> Path:
    """Return a Calidad Sin Sudar style path without overwriting previous files."""
    directory = DOCUMENT_ROOT / str(year) / folder
    base_path = directory / f"{stem}.{extension}"
    if not base_path.exists():
        return base_path

    updated_path = directory / f"{stem}_Actualizada.{extension}"
    if not updated_path.exists():
        return updated_path

    version = 2
    while True:
        candidate = directory / f"{stem}_Actualizada_{version}.{extension}"
        if not candidate.exists():
            return candidate
        version += 1


def _latest_request_number(year: int) -> int:
    """Read the highest PO number currently present in the request-mail folder."""
    if not PO_REQUEST_DIRECTORY.exists():
        return 0

    latest = 0
    for path in PO_REQUEST_DIRECTORY.glob("PO_*.pdf"):
        match = PO_REQUEST_FILENAME.match(path.name)
        if match and int(match.group("year")) == year:
            latest = max(latest, int(match.group("number")))
    return latest


def _request_document_path(reference: str, extension: str = "pdf") -> Path:
    """Return the next request path without overwriting an existing PDF."""
    base_path = PO_REQUEST_DIRECTORY / f"PO_{_safe_part(reference)}.{extension}"
    if not base_path.exists():
        return base_path

    updated_path = PO_REQUEST_DIRECTORY / f"PO_{_safe_part(reference)}_Actualizada.{extension}"
    if not updated_path.exists():
        return updated_path

    version = 2
    while True:
        candidate = PO_REQUEST_DIRECTORY / f"PO_{_safe_part(reference)}_Actualizada_{version}.{extension}"
        if not candidate.exists():
            return candidate
        version += 1


def _acceptance_document_path(reference: str, extension: str = "pdf") -> Path:
    """Return the acceptance PDF path without overwriting an existing file."""
    base_path = ACCEPTANCE_DOCUMENT_DIRECTORY / f"AO_{_safe_part(reference)}.{extension}"
    if not base_path.exists():
        return base_path

    updated_path = ACCEPTANCE_DOCUMENT_DIRECTORY / f"AO_{_safe_part(reference)}_Actualizada.{extension}"
    if not updated_path.exists():
        return updated_path

    version = 2
    while True:
        candidate = ACCEPTANCE_DOCUMENT_DIRECTORY / f"AO_{_safe_part(reference)}_Actualizada_{version}.{extension}"
        if not candidate.exists():
            return candidate
        version += 1


def _quality_mail_document_path(directory: Path, prefix: str, reference: str, extension: str = "pdf") -> Path:
    """Return a quality document path without overwriting existing files."""
    base_path = directory / f"{prefix}{_safe_part(reference)}.{extension}"
    if not base_path.exists():
        return base_path

    updated_path = directory / f"{prefix}{_safe_part(reference)}_Actualizada.{extension}"
    if not updated_path.exists():
        return updated_path

    version = 2
    while True:
        candidate = directory / f"{prefix}{_safe_part(reference)}_Actualizada_{version}.{extension}"
        if not candidate.exists():
            return candidate
        version += 1


def _offer_document_path(reference: str, extension: str = "pdf") -> Path:
    return _quality_mail_document_path(OFFER_DOCUMENT_DIRECTORY, "O_", reference, extension)


def _invoice_document_path(reference: str, extension: str = "pdf") -> Path:
    return _quality_mail_document_path(INVOICE_DOCUMENT_DIRECTORY, "INV_", reference, extension)


def next_offer_reference(db, year: int) -> str:
    """Reserve the next reference after the latest request PDF on disk."""
    db.execute(text("SELECT pg_advisory_xact_lock(hashtext('sgo_offer_reference'))"))
    latest_file_number = _latest_request_number(year)
    latest_db_number = db.execute(
        text("""
            SELECT COALESCE(MAX(CAST(substring(reference from '^[0-9]+') AS integer)), 0)
            FROM offers
            WHERE reference ~ '^[0-9]+'
        """)
    ).scalar_one()
    latest_number = max(latest_file_number, latest_db_number)
    db.execute(
        text("SELECT setval('offer_ref_seq', :value, :is_called)"),
        {"value": max(latest_number, 1), "is_called": latest_number > 0},
    )
    next_number = db.execute(select(models.offer_ref_seq.next_value())).scalar_one()
    return f"{next_number:03d}_{year}"


def _money(value) -> str:
    return f"{float(value or 0):.2f} EUR"


def _date(value) -> str:
    if not value:
        return "-"
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    return str(value)


def _text(value) -> str:
    return escape(str(value if value is not None else "-"))


def _paragraph(value, style):
    return Paragraph(_text(value), style)


def _checksum(path: Path) -> str:
    # Calculates a SHA-256 hash of the generated PDF file.
    # This is used for auditing and to prove the document has not been tampered with.
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def latest_document(db, *, document_type, file_format="pdf", offer_id=None, invoice_id=None):
    query = db.query(models.GeneratedDocument).filter(
        models.GeneratedDocument.document_type == document_type,
        models.GeneratedDocument.file_format == file_format,
    )
    if offer_id is not None:
        query = query.filter(models.GeneratedDocument.offer_id == offer_id)
    if invoice_id is not None:
        query = query.filter(models.GeneratedDocument.invoice_id == invoice_id)
    return query.order_by(models.GeneratedDocument.created_at.desc(), models.GeneratedDocument.id.desc()).first()


def _register_document(db, *, document_type, file_format, path, offer_id=None, invoice_id=None, technician_id=None):
    sha256 = _checksum(path)
    record = models.GeneratedDocument(
        document_type=document_type,
        file_format=file_format,
        file_path=str(path),
        sha256=sha256,
        offer_id=offer_id,
        invoice_id=invoice_id,
        created_by_technician_id=technician_id,
    )
    db.add(record)
    db.commit()
    return record


def _replace_docx_markers(document, replacements):
    """Replace plain-text markers in paragraphs while retaining the template layout."""
    paragraphs = list(document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.extend(cell.paragraphs)

    for paragraph in paragraphs:
        replacement_text = paragraph.text
        for marker, value in replacements.items():
            replacement_text = replacement_text.replace(marker, str(value or "-"))
        if replacement_text != paragraph.text:
            paragraph.text = replacement_text


def _insert_budget_table(document, services):
    """Replace the TABLE marker with the RG-10 budget breakdown."""
    marker_paragraph = next(
        (paragraph for paragraph in document.paragraphs if paragraph.text.strip() == "TABLE"),
        None,
    )
    if marker_paragraph is None:
        raise ValueError("RG-10 template does not contain the TABLE marker")

    table = document.add_table(rows=1, cols=4)
    table.style = "Table Grid"
    for cell, value in zip(table.rows[0].cells, ["Technique", "Hours", "Price/hour", "Total (EUR)"]):
        cell.text = value

    total = 0.0
    for service in services:
        quoted_price = float(service.quoted_price or 0)
        hours = float(service.hours or 0)
        hourly_price = quoted_price / hours if hours else 0.0
        total += quoted_price
        row = table.add_row().cells
        row[0].text = service.service_name
        row[1].text = f"{hours:g}"
        row[2].text = f"{hourly_price:.2f}"
        row[3].text = f"{quoted_price:.2f}"

    total_row = table.add_row().cells
    total_row[0].text = "Total"
    total_row[3].text = f"{total:.2f}"

    marker_element = marker_paragraph._p
    marker_element.addnext(table._tbl)
    marker_element.getparent().remove(marker_element)


def _apply_document_font(document, font_name: str = "Gill Sans"):
    """Apply the requested font to all existing and generated DOCX content."""
    for style in document.styles:
        if hasattr(style, "font"):
            style.font.name = font_name
            style._element.rPr.rFonts.set(qn("w:ascii"), font_name)
            style._element.rPr.rFonts.set(qn("w:hAnsi"), font_name)
            style._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)
            style._element.rPr.rFonts.set(qn("w:cs"), font_name)

    paragraphs = list(document.paragraphs)
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                paragraphs.extend(cell.paragraphs)
    for paragraph in paragraphs:
        for run in paragraph.runs:
            run.font.name = font_name
            run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), font_name)
            run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), font_name)
            run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font_name)
            run._element.get_or_add_rPr().rFonts.set(qn("w:cs"), font_name)


def _find_libreoffice() -> str:
    """Find LibreOffice on Linux, Windows PATH, or common Windows installs."""
    configured_path = os.getenv("LIBREOFFICE_BIN")
    candidates = [configured_path] if configured_path else []
    candidates.extend([
        shutil.which("libreoffice"),
        shutil.which("soffice"),
        os.path.join(os.environ.get("PROGRAMFILES", ""), "LibreOffice", "program", "soffice.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "LibreOffice", "program", "soffice.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "LibreOffice", "program", "soffice.exe"),
    ])
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError(
        "LibreOffice is required to generate RG-10 PDFs. "
        "Install LibreOffice or set LIBREOFFICE_BIN to soffice.exe."
    )


def _render_offer_template(offer, output_path: Path):
    """Fill the RG-10 DOCX template and convert it to the requested PDF path."""
    if not RG10_TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"RG-10 template not found: {RG10_TEMPLATE_PATH}")

    client = offer.client
    services = workflow.active_services(offer)
    technicians = []
    for service in services:
        if service.technician:
            name = f"{service.technician.first_name} {service.technician.last_name}".strip()
            if name not in technicians:
                technicians.append(name)

    document = Document(str(RG10_TEMPLATE_PATH))
    _replace_docx_markers(document, {
        "QUOTE": offer.reference,
        "TECHNICIAN": ", ".join(technicians) or "-",
        "DATE": _date(offer.created_at),
        "CLIENT": f"{client.first_name} {client.last_name}" if client else "-",
        "PROJECT_CODE": offer.codigo_proyecto,
        "CCII": offer.cuenta_interna,
        "IIPP": offer.investigador_principal,
        "TITLE": ", ".join(service.service_name for service in services) or "-",
        "DELIVERY": _date(offer.delivery_date),
    })
    _insert_budget_table(document, services)
    _apply_document_font(document)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temporary_directory:
        temporary_directory = Path(temporary_directory)
        docx_path = temporary_directory / "offer.docx"
        document.save(docx_path)
        libreoffice_bin = _find_libreoffice()
        subprocess.run(
            [
                libreoffice_bin,
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temporary_directory),
                str(docx_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        converted_pdf = temporary_directory / "offer.pdf"
        if not converted_pdf.exists():
            raise RuntimeError("LibreOffice did not produce the RG-10 PDF")
        shutil.copyfile(converted_pdf, output_path)


def _build_pdf(
    path: Path,
    title: str,
    metadata_rows,
    table_headers,
    table_rows,
    total_label: str,
    total: float,
    notes: str | None = None,
    closing_text: str | None = None,
    include_total: bool = True,
    table_col_widths=None,
):
    # Core function that uses ReportLab to draw the PDF layout.
    # It creates a standard A4 page with margins, a title, a metadata table, and a services table.
    path.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=title,
    )

    story = [
        Paragraph("MiNa - IMN / CSIC", styles["Title"]),
        _paragraph(title, styles["Heading2"]),
        Spacer(1, 8),
    ]

    wrapped_metadata_rows = [
        [_paragraph(label, styles["BodyText"]), _paragraph(value, styles["BodyText"])]
        for label, value in metadata_rows
    ]
    meta_table = Table(wrapped_metadata_rows, colWidths=[42 * mm, 120 * mm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f7")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#111827")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    story.extend([meta_table, Spacer(1, 12)])

    data = [
        [_paragraph(cell, styles["BodyText"]) for cell in table_headers],
        *[[_paragraph(cell, styles["BodyText"]) for cell in row] for row in table_rows],
    ]
    if include_total:
        data.append(["", "", _paragraph(total_label, styles["BodyText"]), _paragraph(_money(total), styles["BodyText"])])
    table = Table(data, colWidths=table_col_widths or [72 * mm, 28 * mm, 32 * mm, 30 * mm], repeatRows=1)
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#ebb92f")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]
    if include_total:
        table_style.extend([
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#eef2f7")),
            ("FONTNAME", (2, -1), (-1, -1), "Helvetica-Bold"),
        ])
    table.setStyle(TableStyle(table_style))
    story.append(table)

    if closing_text:
        story.extend([Spacer(1, 16), Paragraph(closing_text, styles["Normal"])])

    story.extend([
        Spacer(1, 16),
        Paragraph(
            "Generated by MiNa's request portal. Stored copy is kept on the IMN server for traceability and ISO 9001 audit purposes.",
            styles["Normal"],
        ),
    ])
    doc.build(story)


def generate_request_pdf(db, offer, technician_id=None):
    client = offer.client
    year = (offer.created_at or datetime.now()).year
    reference = offer.reference or f"offer_{offer.id}"
    path = _request_document_path(reference)
    table_rows = [
        [service.service_name, service.comment or "-"]
        for service in workflow.active_services(offer)
    ]
    metadata_rows = [
        ["Reference", reference],
        ["Date", _date(offer.created_at)],
        ["Client", f"{client.first_name} {client.last_name}" if client else "-"],
        ["Email", client.email if client else "-"],
        ["Entity", client.entity if client else "-"],
        ["Project code", offer.codigo_proyecto or "-"],
        ["Internal account", offer.cuenta_interna or "-"],
        ["Principal investigator", offer.investigador_principal or "-"],
    ]
    _build_pdf(
        path,
        f"Service request PO_{reference}",
        metadata_rows,
        ["Requested service", "Comment"],
        table_rows,
        "Estimated total",
        0.0,
        include_total=False,
        table_col_widths=[72 * mm, 90 * mm],
        closing_text="MiNa staff will attend to your request and you will receive an email once an offer has been generated.",
    )
    return _register_document(db, document_type="request", file_format="pdf", path=path, offer_id=offer.id, technician_id=technician_id)


def generate_offer_pdf(db, offer, technician_id=None):
    reference = offer.reference or f"offer_{offer.id}"
    path = _offer_document_path(reference)
    _render_offer_template(offer, path)
    return _register_document(db, document_type="offer", file_format="pdf", path=path, offer_id=offer.id, technician_id=technician_id)


def generate_acceptance_pdf(db, offer, technician_id=None):
    client = offer.client
    manager = offer.manager
    year = (offer.created_at or datetime.now()).year
    reference = offer.reference or f"offer_{offer.id}"
    path = _acceptance_document_path(reference)
    table_rows = [
        [
            service.service_name,
            f"{service.hours:g}",
            service.technician.first_name + " " + service.technician.last_name if service.technician else "-",
            _money(service.quoted_price),
        ]
        for service in workflow.active_services(offer)
    ]
    metadata_rows = [
        ["Reference", reference],
        ["Acceptance date", datetime.now().strftime("%d/%m/%Y")],
        ["Client", f"{client.first_name} {client.last_name}" if client else "-"],
        ["Email", client.email if client else "-"],
        ["Entity", client.entity if client else "-"],
        ["Principal investigator", offer.investigador_principal or "-"],
        ["Project code", offer.codigo_proyecto or "-"],
        ["Internal account", offer.cuenta_interna or "-"],
        ["Offer Manager", f"{manager.first_name} {manager.last_name}" if manager else "-"],
        ["Status", workflow.ACCEPTED],
    ]
    _build_pdf(
        path,
        f"Offer acceptance AO_{reference}",
        metadata_rows,
        ["Accepted service", "Hours", "Technician", "Price"],
        table_rows,
        "Accepted total",
        workflow.sum_offer_total(offer),
        "The client accepted the quotation through SGO.",
    )
    return _register_document(db, document_type="acceptance", file_format="pdf", path=path, offer_id=offer.id, technician_id=technician_id)


def generate_invoice_pdf(db, invoice, technician_id=None):
    year = (invoice.created_at or datetime.now()).year
    path = _invoice_document_path(f"{invoice.id:04d}_{year}")
    client = invoice.client
    technician = invoice.technician

    table_rows = []
    for offer in invoice.offers:
        for service in workflow.active_services(offer):
            table_rows.append([
                f"{offer.reference or offer.id} - {service.service_name}",
                f"{service.hours:g}",
                service.technician.first_name + " " + service.technician.last_name if service.technician else "-",
                _money(service.quoted_price),
            ])

    metadata_rows = [
        ["Invoice", f"#{invoice.id}"],
        ["Date", _date(invoice.created_at)],
        ["Client", f"{client.first_name} {client.last_name}" if client else "-"],
        ["Email", client.email if client else "-"],
        ["Entity", client.entity if client else "-"],
        ["Technician", f"{technician.first_name} {technician.last_name}" if technician else "-"],
        ["Status", invoice.status],
    ]
    _build_pdf(
        path,
        f"Invoice #{invoice.id}",
        metadata_rows,
        ["Service", "Hours", "Technician", "Price"],
        table_rows,
        "Invoice total",
        invoice.total_price,
        invoice.comment,
    )
    return _register_document(db, document_type="invoice", file_format="pdf", path=path, invoice_id=invoice.id, technician_id=technician_id)
