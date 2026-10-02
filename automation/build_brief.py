# -*- coding: utf-8 -*-
"""Arma el JSON y los gráficos del brief semanal NOVA (fase Despliegue · CRISP-DM)."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = Path(__file__).parent / "output"
FIG = OUT / "figuras"
COLOR = "#1B3A4B"
ACCENT = "#8C3A2F"


def _pesos(v: float) -> str:
    if v >= 1e9:
        return f"${v / 1e9:.2f} mil millones".replace(".", ",")
    if v >= 1e6:
        return f"${v / 1e6:.1f} millones".replace(".", ",")
    return f"${v:,.0f}".replace(",", ".")


def cargar_ficha() -> dict:
    ruta = DATA / "ficha_nova.json"
    if not ruta.exists():
        print(f"ERROR: falta {ruta}")
        sys.exit(1)
    return json.loads(ruta.read_text(encoding="utf-8"))


def grafico_ventas(sem: pd.DataFrame) -> None:
    tot = sem.groupby("semana", as_index=False)["ventas"].sum()
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.plot(tot["semana"], tot["ventas"], color=COLOR, lw=2)
    ax.set_title("NOVA · ventas semanales (total)")
    ax.set_ylabel("COP")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "ventas_semanales.png", dpi=160)
    plt.close()


def grafico_margen(ficha: dict) -> None:
    canales = ["Tienda", "E-commerce", "Marketplace"]
    vals = [
        ficha["margen_tienda"] * 100,
        ficha["margen_ecommerce"] * 100,
        ficha["margen_marketplace"] * 100,
    ]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.barh(canales, vals, color=[COLOR, "#3D6B58", ACCENT])
    ax.set_xlabel("Margen %")
    ax.set_title("Margen por canal · referencia agosto")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "margen_canal.png", dpi=160)
    plt.close()


def grafico_mape(pron: pd.DataFrame | None) -> None:
    if pron is None or pron.empty:
        return
    sub = pron[(pron["serie"] == "NOVA total") & (pron["uso"] == "paso")].dropna(subset=["pronostico"])
    filas = []
    for modelo, parte in sub.groupby("modelo"):
        real = parte["real"].to_numpy()
        pred = parte["pronostico"].to_numpy()
        mape = (abs(pred - real) / real).mean() * 100
        filas.append((modelo, mape))
    if not filas:
        return
    filas.sort(key=lambda x: x[1])
    fig, ax = plt.subplots(figsize=(9.2, 4.4))
    ax.barh([f[0] for f in filas][::-1], [f[1] for f in filas][::-1], color=COLOR)
    ax.set_xlabel("MAPE % · semana siguiente")
    ax.set_title("Pronóstico · error por modelo")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIG / "mape_modelos.png", dpi=160)
    plt.close()


def resumen_pronostico(pron: pd.DataFrame | None) -> dict:
    if pron is None or pron.empty:
        return {}
    h = pron[(pron["serie"] == "NOVA total") & (pron["uso"] == "horizonte")]
    if h.empty:
        return {}
    ult = h.groupby("modelo")["pronostico"].last()
    return {
        "modelos_horizonte_8s": {k: float(v) for k, v in ult.items()},
        "modelo_min_mape": None,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    ficha = cargar_ficha()
    sem = pd.read_csv(DATA / "ventas_semanales.csv", parse_dates=["semana"])
    pron_path = DATA / "pronosticos.csv"
    pron = pd.read_csv(pron_path) if pron_path.exists() else None

    grafico_ventas(sem)
    grafico_margen(ficha)
    grafico_mape(pron)

    run_date = datetime.now().strftime("%Y-%m-%d")
    summary = {
        "run_date": run_date,
        "data_through": ficha.get("hasta", run_date),
        "empresa": "NOVA S.A.S.",
        "asignatura": "Inteligencia de Negocios y Data Storytelling",
        "crisp_fase": "Despliegue",
        "ventas_12m_cop": ficha["ventas_12m"],
        "ventas_12m_texto": _pesos(ficha["ventas_12m"]),
        "crecimiento_12m_pct": round(ficha["crecimiento_12m"] * 100, 2),
        "caida_ult8_vs_prev8_pct": round(ficha["caida_ult8_vs_prev8"] * 100, 2),
        "margen_tienda_pct": round(ficha["margen_tienda"] * 100, 2),
        "margen_ecommerce_pct": round(ficha["margen_ecommerce"] * 100, 2),
        "margen_marketplace_pct": round(ficha["margen_marketplace"] * 100, 2),
        "clientes_panel": ficha["clientes_panel"],
        "pronostico": resumen_pronostico(pron),
        "graficos": [
            "ventas_semanales.png",
            "margen_canal.png",
            "mape_modelos.png",
        ],
    }
    (OUT / "nova_brief.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Brief listo:", OUT / "nova_brief.json")


if __name__ == "__main__":
    main()
