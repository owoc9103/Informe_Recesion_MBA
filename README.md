# Brief ejecutivo NOVA · Inteligencia de Negocios y Data Storytelling (MBA)

Informe semanal para comité: datos del caso **NOVA S.A.S.**, tres gráficos locales, narrativa con **Groq (Qwen)**, envío con **Gmail**, orquestado en **GitHub Actions**.

Misma arquitectura que [Informe_recesion](https://github.com/owoc9103/Informe_recesion) (ML · probabilidad de recesión FRED), adaptada al MBA: **sin FRED**, CSV en `data/` generados con `datos/generar_nova.py` en [clase_MBA](https://github.com/owoc9103/clase_MBA).

---

## Qué hace

Cada lunes (repo del profesor) o **viernes 7:00 Colombia** (fork del estudiante), GitHub Actions:

1. Lee `ficha_nova.json`, ventas semanales y pronósticos en `data/`.
2. Calcula KPIs y dibuja tres PNG.
3. Escribe `automation/output/nova_brief.json`.
4. **Qwen** redacta el memorando en español.
5. **Gmail** envía el correo con gráficos incrustados.

---

## Arranque rápido

### Fork (entrega MBA)

1. Fork de este repo en tu cuenta.
2. **Secretos** (Settings → Secrets → Actions): `GROQ_API_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_PORT`, `EMAIL_TO`.
3. **Workflow permissions:** Read and write.
4. **Actions** habilitado en el fork.
5. **Único cambio de código:** en `.github/workflows/weekly_nova_brief.yml`, cron `0 12 * * 5` (viernes 7:00 Colombia).
6. **Run workflow** para probar.

### Local (Windows)

```powershell
.\ejecutar_local.ps1
```

Claves en `.env` (ver `.env.ejemplo`). No subir `.env`.

---

## Estructura

```
├── automation/
│   ├── build_brief.py
│   ├── generate_email.py
│   └── output/
├── data/
│   ├── ficha_nova.json
│   ├── ventas_semanales.csv
│   └── pronosticos.csv
├── .github/workflows/weekly_nova_brief.yml
├── ejecutar_local.ps1
├── requirements.txt
└── README.md
```

Presentación y guía paso a paso: carpeta `Sesion_IA_Decisiones` en [clase_MBA](https://github.com/owoc9103/clase_MBA).
