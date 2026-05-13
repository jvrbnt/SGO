from pathlib import Path

from backend.pdf_documents import _build_pdf, _safe_part


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
