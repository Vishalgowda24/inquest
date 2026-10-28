from simulator.core.export import write_export
from simulator.scenarios.cause_alerts_2_4 import generate as cause_alerts_2_4
from simulator.scenarios.unordered_plausible_alerts import generate as unordered_plausible_alerts


def _alert_order(data):
    events = [item for item in data.logs if item.attributes.get("alert_emission") is True]
    return [item.service for item in sorted(events, key=lambda item: (item.timestamp, item.id))]


def test_cause_alert_is_at_position_two_through_four_and_export_is_opaque(tmp_path):
    for seed in range(32, 52):
        data = cause_alerts_2_4(seed)
        assert data.truth["cause_alert_position"] in {2, 3, 4}
        assert _alert_order(data).index("database") + 1 == data.truth["cause_alert_position"]
        assert data.manifest.scenario_id.startswith("scn_")
    data = cause_alerts_2_4(32)
    export = tmp_path / data.manifest.scenario_id / "export"
    write_export(data, export, tmp_path / "sim_truth" / "truth.json")
    text = "\n".join(path.read_text(encoding="utf-8") for path in export.rglob("*") if path.is_file())
    assert "cause_alerts_2_4" not in text
    assert "injected_fault" not in text


def test_unordered_alerts_balance_cause_position_independently_of_fault(tmp_path):
    positions = []
    for seed in range(32, 52):
        data = unordered_plausible_alerts(seed)
        order = _alert_order(data)
        position = order.index("database") + 1
        assert position == data.truth["cause_alert_position"]
        positions.append(position)
        assert data.truth["alert_order_independent_of_causality"] is True
    assert {position: positions.count(position) for position in range(1, 5)} == {1: 5, 2: 5, 3: 5, 4: 5}
    data = unordered_plausible_alerts(32)
    export = tmp_path / data.manifest.scenario_id / "export"
    write_export(data, export, tmp_path / "sim_truth" / "truth.json")
    text = "\n".join(path.read_text(encoding="utf-8") for path in export.rglob("*") if path.is_file())
    assert "unordered_plausible_alerts" not in text
    assert "injected_fault" not in text
