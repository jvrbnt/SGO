"""Minimal standalone result pages shown after following an e-mail link."""
from html import escape

from fastapi.responses import HTMLResponse


def result_page(title: str, message: str, ok: bool = True, status_code: int = 200) -> HTMLResponse:
    color = "#15803d" if ok else "#b91c1c"
    icon = "&#10003;" if ok else "&#10007;"
    body = f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)} - MiNa</title>
<style>
body{{font-family:Arial,sans-serif;background:#f1f5f9;margin:0;display:flex;min-height:100vh;align-items:center;justify-content:center}}
.card{{background:#fff;padding:40px 48px;max-width:460px;text-align:center;box-shadow:0 4px 18px rgba(0,0,0,.12)}}
.icon{{font-size:56px;color:{color};line-height:1}}
h1{{color:#0f172a;font-size:24px;margin:16px 0 8px}}
p{{color:#475569;line-height:1.5}}
a{{display:inline-block;margin-top:18px;color:#fff;background:#0f172a;padding:10px 22px;text-decoration:none;font-weight:bold}}
</style></head><body><div class="card"><div class="icon">{icon}</div>
<h1>{escape(title)}</h1><p>{escape(message)}</p><a href="/login">MiNa</a></div></body></html>"""
    return HTMLResponse(body, status_code=status_code)
