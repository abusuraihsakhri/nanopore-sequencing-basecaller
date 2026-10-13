"""Regression coverage for validated payloads, privacy guard and both CLIs."""
import csv
import pytest
from fastapi.testclient import TestClient

from agents.api import app
from agents.base import AuditTrail, SecurityException
from agents.models import SystemTaskPayload
from agents.supervisor import SystemSupervisor
from cli import main as root_main
from nanopore_basecaller.cli import main as legacy_main


def test_attributes_are_checked_for_sensitive_identifiers():
    payload = SystemTaskPayload(
        task_id="TEST-1", target_identifier="SPECIMEN-1", primary_metric=1,
        attributes={"nested": {"email": "example.patient@example.org"}},
    )
    with pytest.raises(SecurityException):
        SystemSupervisor().process_task(payload)


@pytest.mark.parametrize("field,value", [
    ("task_id", ""), ("target_identifier", ""),
    ("task_id", "x" * 129), ("status_descriptor", ""),
])
def test_reject_invalid_identifiers(field, value):
    data = {"task_id": "T", "target_identifier": "S", "primary_metric": 1}
    data[field] = value
    with pytest.raises(ValueError):
        SystemTaskPayload(**data)


def test_sensitive_api_payload_rejected_without_echo():
    client = TestClient(app)
    response = client.post("/api/audit", json={
        "task_id": "T", "target_identifier": "SPECIMEN-1",
        "primary_metric": 1, "attributes": {"contact": "patient@example.org"},
    })
    assert response.status_code == 422
    assert "patient@example.org" not in response.text


def test_api_normal_audit_and_health():
    client = TestClient(app)
    assert client.get("/health").status_code == 200
    response = client.post("/api/audit", json={
        "task_id": "T", "target_identifier": "SPECIMEN-1",
        "primary_metric": 10, "secondary_metric": 4,
    })
    assert response.status_code == 200
    assert response.json()["overall_urgency"] == "ROUTINE"


def test_exposed_audit_snapshots_cannot_be_mutated():
    audit = AuditTrail(secret_key="unit-test-key")
    audit.log("tester", "worker", "START", {"status": "OK"})
    snapshot = audit.get_trail()
    snapshot[0]["payload_hash"] = "tampered"
    snapshot.append({})
    assert len(audit.get_trail()) == 1
    assert audit.verify_integrity()


def test_batch_rejects_missing_required_column(tmp_path):
    source = tmp_path / "missing.csv"
    source.write_text("task_id,secondary_metric\nT,1\n", encoding="utf-8")
    assert root_main(["batch", "-i", str(source), "-o", str(tmp_path / "out.csv")]) == 1


def test_batch_skips_unrecognized_boolean_and_malformed_record(tmp_path):
    source = tmp_path / "tasks.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag\n"
        "T1,S1,4,3,False\n"
        "T2,S2,4,3,perhaps\n"
        "T3,S3,4,3,False,extraneous\n", encoding="utf-8",
    )
    out = tmp_path / "result.csv"
    assert root_main(["batch", "-i", str(source), "-o", str(out)]) == 0
    with out.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 1
    assert rows[0]["overall_urgency"] == "ROUTINE"


def test_legacy_batch_false_flag_does_not_trigger_critical(tmp_path):
    source = tmp_path / "legacy.csv"
    source.write_text(
        "task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\n"
        "T,S,2,2,False,NOMINAL\n", encoding="utf-8",
    )
    out = tmp_path / "legacy_out.csv"
    assert legacy_main(["batch", "-i", str(source), "-o", str(out)]) == 0
    with out.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    assert rows[0]["overall_status"] == "NOMINAL_OPTIMAL"
