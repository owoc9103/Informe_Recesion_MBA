# Informe automático NOVA · Inteligencia de Negocios y Data Storytelling

Brief semanal para comité: datos del caso NOVA, gráficos locales, narrativa con **Groq**, envío con **Gmail**, orquestado en **GitHub Actions**.

No usa FRED: los CSV en `data/` vienen del caso pedagógico (`datos/generar_nova.py` en el repo MBA).

## Flujo

1. `automation/build_brief.py` → `nova_brief.json` + PNG en `automation/output/figuras/`
2. `automation/generate_email.py` → HTML + correo (si hay secretos)

## Entrega (fork)

Igual que el taller de recesión en ML: fork propio, secretos en GitHub, **único cambio de código** el cron a viernes 7:00 Colombia (`0 12 * * 5`).

Secretos: `GROQ_API_KEY`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_PORT`, `EMAIL_TO`.

Repositorio del curso: [Informe_Recesion_MBA](https://github.com/owoc9103/Informe_Recesion_MBA) (brief NOVA · MBA). Material relacionado en [clase_MBA](https://github.com/owoc9103/clase_MBA).
