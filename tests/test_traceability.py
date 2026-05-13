from backend.routers.traceability import _csv_safe


def test_csv_safe_prevents_spreadsheet_formula_injection():
    assert _csv_safe("=1+1") == "'=1+1"
    assert _csv_safe("+cmd") == "'+cmd"
    assert _csv_safe("-10") == "'-10"
    assert _csv_safe("@SUM(A1:A2)") == "'@SUM(A1:A2)"
    assert _csv_safe("normal text") == "normal text"
    assert _csv_safe(None) == ""
