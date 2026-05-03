"""Punto de entrada principal de kpi-pulse."""
import argparse, csv, os
from datetime import datetime
from pathlib import Path

import yaml
from .connector import DBConnector
from .evaluator import evaluate
from .alerts import send_slack, send_email


def run(config_path="config.yaml", verbose=False, alerts_only=False):
    with open(config_path) as f:
        config = yaml.safe_load(f)

    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando kpi-pulse...\n")

    db = DBConnector(config["database"])
    if not db.test_connection():
        print("  No se pudo conectar a la base de datos.")
        return

    results, active_alerts = [], []

    for m in config.get("metrics", []):
        if verbose:
            print(f"  Ejecutando: {m['name']}...")
        value = db.run_query(m["query"])
        result = evaluate(m["name"], value, m.get("alert_if", "False"), m.get("description", ""))
        results.append(result)
        if not alerts_only or result.is_alert:
            print(result.message)
        if result.is_alert:
            active_alerts.append({"name": result.name, "value": result.value, "description": result.description})

    if active_alerts:
        alerts_cfg = config.get("alerts", {})
        slack_ok = send_slack(os.environ.get("SLACK_WEBHOOK_URL", alerts_cfg.get("slack_webhook", "")), active_alerts)
        email_ok = send_email(alerts_cfg.get("email", ""), active_alerts)
        sent_to = []
        if slack_ok: sent_to.append("Slack")
        if email_ok: sent_to.append("email")
        if sent_to:
            print(f"\n  → {len(active_alerts)} alerta(s). Notificación enviada a {', '.join(sent_to)}.")
    else:
        print("\n  → Todo dentro de los rangos esperados.")

    Path("reports").mkdir(exist_ok=True)
    report_path = f"reports/{datetime.now().strftime('%Y-%m-%d')}.csv"
    with open(report_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["timestamp","name","value","is_alert","description"])
        w.writeheader()
        for r in results:
            w.writerow({"timestamp": datetime.now().isoformat(), "name": r.name,
                        "value": r.value, "is_alert": r.is_alert, "description": r.description})
    print(f"  → Reporte guardado en {report_path}\n")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config.yaml")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--alerts-only", action="store_true")
    args = p.parse_args()
    run(args.config, args.verbose, args.alerts_only)
