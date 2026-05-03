"""Envío de alertas por Slack y email."""
import json, os, smtplib
from email.mime.text import MIMEText

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def send_slack(webhook_url: str, alerts: list) -> bool:
    if not HAS_REQUESTS or not webhook_url:
        return False
    lines = [f"*kpi-pulse — {len(alerts)} alerta(s) activa(s):*"]
    for a in alerts:
        lines.append(f"• *{a['name']}*: {a['value']}  —  {a['description']}")
    try:
        r = requests.post(webhook_url, data=json.dumps({"text": "\n".join(lines)}), timeout=5)
        return r.status_code == 200
    except Exception:
        return False


def send_email(recipient: str, alerts: list) -> bool:
    user = os.environ.get("SMTP_USER", "")
    password = os.environ.get("SMTP_PASS", "")
    if not user or not password:
        return False
    body = f"kpi-pulse detectó {len(alerts)} alerta(s):\n\n"
    for a in alerts:
        body += f"- {a['name']}: {a['value']} ({a['description']})\n"
    msg = MIMEText(body)
    msg["Subject"] = f"[kpi-pulse] {len(alerts)} alerta(s)"
    msg["From"] = user
    msg["To"] = recipient
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as s:
            s.starttls()
            s.login(user, password)
            s.sendmail(user, recipient, msg.as_string())
        return True
    except Exception:
        return False
