# kpi-pulse

Monitor de KPIs desde SQL con alertas automáticas.

Lo construí porque una vez tuvimos datos corruptos por 3 días y el dashboard seguía mostrando todo verde. Nadie se dio cuenta hasta que llegó el reporte del viernes. Este proyecto es básicamente la solución a ese problema.

---

## ¿Qué hace?

Conecta a tu base de datos, corre las queries que defines, evalúa si los valores están dentro de lo esperado y te avisa si algo está mal. Nada más, nada menos.

- Soporte para PostgreSQL, MySQL y SQLite
- Alertas por Slack y email
- Configuración en YAML (sin tocar el código)
- Reporte diario en CSV

---

## Instalación

```bash
git clone https://github.com/marcelo-sosa-data/kpi-pulse.git
cd kpi-pulse
pip install -r requirements.txt
```

Crea un archivo `.env` con tus credenciales:

```bash
DB_PASSWORD=tu_password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # opcional
```

---

## Configuración

Define tus métricas en `config.yaml`:

```yaml
database:
  type: postgresql
  host: localhost
  port: 5432
  dbname: ventas_db
  user: marcelo

metrics:
  - name: ventas_del_dia
    query: >
      SELECT COALESCE(SUM(amount), 0)
      FROM orders
      WHERE DATE(created_at) = CURRENT_DATE
    alert_if: "value < 10000"
    description: "Ventas totales de hoy"

  - name: tasa_conversion
    query: >
      SELECT ROUND(
        COUNT(CASE WHEN status = 'converted' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0),
      2)
      FROM leads
      WHERE DATE(created_at) = CURRENT_DATE
    alert_if: "value < 5.0"
    description: "% de leads que convierten"

  - name: pedidos_trabados
    query: >
      SELECT COUNT(*)
      FROM orders
      WHERE status = 'pending'
      AND created_at < NOW() - INTERVAL '2 hours'
    alert_if: "value > 50"
    description: "Pedidos pendientes por más de 2 horas"

alerts:
  slack_webhook: ${SLACK_WEBHOOK_URL}
  email: marcelo@empresa.com
```

---

## Uso

```bash
# Corre todos los checks
python -m kpi_pulse.monitor

# Solo muestra lo que está fallando
python -m kpi_pulse.monitor --alerts-only

# Con más detalle
python -m kpi_pulse.monitor --verbose
```

Output:

```
[2026-05-03 08:00:01] Iniciando kpi-pulse...

  ✓ ventas_del_dia        →  $47,230    OK
  ✗ tasa_conversion       →  3.8%       ALERTA (esperado >= 5.0%)
  ✓ pedidos_trabados      →  12         OK

  → 1 alerta activa. Notificación enviada a Slack.
  → Reporte guardado en reports/2026-05-03.csv
```

---

## Estructura del proyecto

```
kpi-pulse/
├── kpi_pulse/
│   ├── monitor.py      # punto de entrada
│   ├── connector.py    # manejo de la conexión SQL
│   ├── evaluator.py    # lógica de evaluación de alertas
│   └── alerts.py       # Slack y email
├── tests/
├── config.yaml         # tus métricas van acá
├── .env.example
└── requirements.txt
```

---

## Stack

Python · SQLAlchemy · PyYAML · requests

---

## Pendiente

- [ ] Integración con Airflow (como sensor)
- [ ] Soporte para BigQuery
- [ ] Detección de anomalías estadísticas (no solo umbrales fijos)
