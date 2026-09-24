from pathlib import Path

from backend import pdf_documents
from backend.pdf_documents import _build_pdf, _quality_document_path, _safe_part


def test_safe_part_removes_path_characters():
    assert _safe_part("../O 001/2026") == "O_001_2026"
    assert _safe_part("") == "document"


def test_build_pdf_creates_pdf_file(tmp_path):
    output = tmp_path / "offer.pdf"
    _build_pdf(
        output,
        "Offer <001>",
        [["Client", "Example <Client>"], ["Status", "quoted"]],
        ["Service", "Hours", "Technician", "Price"],
        [["SEM", "1", "Tech", "10.00 EUR"]],
        "Total",
        10.0,
        "Audit note",
    )

    assert output.exists()
    assert output.read_bytes().startswith(b"%PDF")


def test_quality_document_path_uses_original_naming_and_updated_suffix(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_documents, "DOCUMENT_ROOT", tmp_path)

    first = _quality_document_path(2026, "offers", "O_001_2026")
    assert first == tmp_path / "2026" / "offers" / "O_001_2026.pdf"

    first.parent.mkdir(parents=True)
    first.write_bytes(b"%PDF first")
    second = _quality_document_path(2026, "offers", "O_001_2026")
    assert second == tmp_path / "2026" / "offers" / "O_001_2026_Actualizada.pdf"

    second.write_bytes(b"%PDF second")
    third = _quality_document_path(2026, "offers", "O_001_2026")
    assert third == tmp_path / "2026" / "offers" / "O_001_2026_Actualizada_2.pdf"


def test_latest_request_number_reads_mail_request_folder(tmp_path, monkeypatch):
    monkeypatch.setattr(pdf_documents, "PO_REQUEST_DIRECTORY", tmp_path)
    (tmp_path / "PO_001_2026.pdf").write_bytes(b"%PDF first")
    (tmp_path / "PO_009_2025.pdf").write_bytes(b"%PDF old")
    (tmp_path / "PO_not-a-number_2026.pdf").write_bytes(b"%PDF invalid")

    assert pdf_documents._latest_request_number(2026) == 1
