from kpi_pulse.evaluator import evaluate

def test_ok():
    r = evaluate("ventas", 50000, "value < 10000", "ventas")
    assert r.is_alert is False

def test_alerta():
    r = evaluate("ventas", 3000, "value < 10000", "ventas")
    assert r.is_alert is True

def test_none_es_alerta():
    r = evaluate("ventas", None, "value < 10000", "ventas")
    assert r.is_alert is True
