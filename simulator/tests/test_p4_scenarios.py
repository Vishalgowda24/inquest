from simulator.scenarios.concurrent_causes import generate as concurrent_causes
from simulator.scenarios.noisy_alerts import generate as noisy_alerts
from simulator.scenarios.partial_graph import generate as partial_graph
from simulator.scenarios.red_herring_hard import generate as red_herring_hard


def test_p4_ids_are_opaque_and_truth_is_separate():
    for generator, name in (
        (concurrent_causes, "concurrent_causes"),
        (noisy_alerts, "noisy_alerts"),
        (partial_graph, "partial_graph"),
        (red_herring_hard, "red_herring_hard"),
    ):
        data = generator(11)
        assert data.manifest.scenario_id.startswith("scn_")
        assert name not in data.manifest.scenario_id
        assert name in data.truth["scenario_name"]


def test_concurrent_faults_are_recorded_as_two_truth_causes():
    data = concurrent_causes(11)
    faults = data.truth["injected_fault"]
    assert [fault["service"] for fault in faults] == ["payments", "inventory"]
    assert faults[0]["start_step"] < faults[1]["start_step"]
    assert data.metrics
    # Both independently faulty services emit metric windows from the same
    # parameter-driven simulation run; downstream effects are not hand-authored.
    assert {point.service for point in data.metrics} >= {"payments", "inventory", "checkout", "database"}


def test_alert_noise_is_explicit_and_metrics_untouched():
    data = noisy_alerts(11)
    alerts = [event for event in data.logs if event.attributes.get("alert_emission")]
    assert {event.service for event in alerts} == set(data.manifest.services)
    assert len({event.timestamp for event in alerts}) > 1
    assert all(point.service == "database" or point.value >= 0 for point in data.metrics)


def test_partial_graph_marks_collection_completeness_and_omission():
    data = partial_graph(11)
    assert data.manifest.dependency_graph_complete is False
    assert "payments->database" in data.truth["omitted_dependency_edges"]
    assert not any(edge.caller == "payments" and edge.callee == "database" for edge in data.dependencies)


def test_red_herring_hard_contains_both_decoys_and_real_change():
    data = red_herring_hard(11)
    assert data.truth["injected_fault"]["service"] == "payments"
    assert {event.service for event in data.events} == {"payments", "inventory"}
    assert any(edge.callee == "database" for edge in data.dependencies)
