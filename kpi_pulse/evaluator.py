"""
Evalúa si el valor de una métrica activa una alerta.
La condición se define en YAML como una expresión simple: "value < 10000".
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class MetricResult:
    name: str
    value: Optional[float]
    description: str
    alert_if: str
    is_alert: bool
    message: str


def evaluate(name: str, value: Optional[float], alert_if: str, description: str) -> MetricResult:
    if value is None:
        return MetricResult(name, None, description, alert_if, True,
                            "sin datos — la query devolvió NULL")
    try:
        # eval controlado, solo expone 'value'
        triggered = eval(alert_if, {"__builtins__": {}}, {"value": value})
    except Exception as e:
        return MetricResult(name, value, description, alert_if, True,
                            f"error evaluando condición: {e}")

    status = "✗" if triggered else "✓"
    detail = f"ALERTA ({alert_if})" if triggered else "OK"
    msg = f"  {status} {name:<28} →  {str(value):<12} {detail}"
    return MetricResult(name, value, description, alert_if, triggered, msg)
