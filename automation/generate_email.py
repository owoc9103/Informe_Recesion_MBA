# -*- coding: utf-8 -*-
"""Redacta y envía el brief ejecutivo NOVA con Groq (JSON → HTML → Gmail)."""

from __future__ import annotations

import json
import os
import smtplib
import sys
import time
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from groq import Groq

OUT = Path(__file__).parent / "output"
FIG = OUT / "figuras"
MODELO = "qwen/qwen3-32b"
MAX_IMAGENES = 0


def cargar_env() -> None:
    ruta = Path(__file__).resolve().parents[1] / ".env"
    if not ruta.exists():
        return
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        texto = linea.strip()
        if not texto or texto.startswith("#") or "=" not in texto:
            continue
        clave, valor = texto.split("=", 1)
        clave, valor = clave.strip(), valor.strip().strip('"')
        if valor and clave not in os.environ:
            os.environ[clave] = valor


cargar_env()


def load_summary() -> dict:
    path = OUT / "nova_brief.json"
    if not path.exists():
        print(f"ERROR: {path} no existe. Ejecute build_brief.py primero.")
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def generate_analysis(summary: dict) -> dict:
    if not os.environ.get("GROQ_API_KEY"):
        print("ERROR: GROQ_API_KEY")
        sys.exit(1)
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    run_date = summary.get("run_date", datetime.now().strftime("%Y-%m-%d"))
    prompt = f"""Eres analista senior de inteligencia de negocios en NOVA S.A.S.
Redacta en español un brief semanal para comité ejecutivo (MBA · data storytelling).

FECHA DE CORRIDA: {run_date}
CORTE DE DATOS: {summary.get("data_through")}

Marco CRISP-DM: fase **Despliegue** — el número y la narrativa llegan solos a quien decide.

JSON del caso:
{json.dumps(summary, indent=2, ensure_ascii=False)}

Incluye referencias a gráficos con <img src="cid:chart_0"> (ventas), cid:chart_1 (margen), cid:chart_2 (MAPE modelos).

Secciones (HTML con estilo inline, tono ejecutivo, sin emojis):
1. Asunto en clave "NOVA · brief semanal · [fecha]"
2. Resumen para comité (4 bullets: ventas 12m, caída reciente 8s, margen marketplace vs tienda, lectura de pronóstico)
3. Qué está pasando (descriptivo)
4. Qué implica para la decisión de segmentos (enlace con Sesión 1)
5. Pronóstico y certeza (predictivo; menciona dispersión de modelos si aplica)
6. Riesgos explícitos (2–3)
7. Qué vigilar la próxima semana
8. Cierre: decisión recomendada con hedging ("consistente con", no órdenes)

Extensión: 700–1000 palabras. Responde JSON: {{"subject": "...", "html_body": "..."}}
"""
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=MODELO,
                max_completion_tokens=6000,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.choices[0].message.content or "{}"
            return json.loads(text)
        except Exception as exc:
            if attempt == 3:
                raise
            time.sleep(2 ** (attempt + 1))
            print(f"Reintento Groq: {exc}")
    return {}


def send_email(subject: str, html_body: str, charts: list[str]) -> None:
    user = os.environ.get("MAIL_USERNAME")
    pwd = os.environ.get("MAIL_PASSWORD")
    port = int(os.environ.get("MAIL_PORT", "587"))
    dest = os.environ.get("EMAIL_TO", "")
    if not all([user, pwd, dest]):
        print("Envío omitido (faltan MAIL_* o EMAIL_TO). HTML guardado.")
        return
    msg = MIMEMultipart("related")
    msg["Subject"] = subject
    msg["From"] = user
    msg["To"] = dest
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    for i, nombre in enumerate(charts):
        ruta = FIG / nombre
        if not ruta.exists():
            continue
        img = MIMEImage(ruta.read_bytes())
        img.add_header("Content-ID", f"<chart_{i}>")
        img.add_header("Content-Disposition", "inline", filename=nombre)
        msg.attach(img)
    with smtplib.SMTP("smtp.gmail.com", port) as smtp:
        smtp.starttls()
        smtp.login(user, pwd)
        smtp.sendmail(user, [d.strip() for d in dest.split(",") if d.strip()], msg.as_string())
    print("Correo enviado.")


def main() -> None:
    summary = load_summary()
    charts = summary.get("graficos", [])
    summary["charts"] = charts
    result = generate_analysis(summary)
    subject = result.get("subject", f"NOVA · brief · {summary.get('run_date')}")
    html = result.get("html_body", "<p>Sin cuerpo</p>")
    (OUT / f"email_{summary.get('run_date')}.html").write_text(html, encoding="utf-8")
    (OUT / "email_result.json").write_text(
        json.dumps({"subject": subject, "charts": charts}, indent=2), encoding="utf-8"
    )
    send_email(subject, html, charts)


if __name__ == "__main__":
    main()
