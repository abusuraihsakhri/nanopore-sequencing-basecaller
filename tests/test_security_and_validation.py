"""
Security and input validation tests for Nanopore Sequencing Basecaller.
"""
import sys
import os
import math
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import PHIGuard, AuditLogger, SecurityException, AuditTrail
from agents.models import SystemTaskPayload, UrgencyLevel
from agents.supervisor import SystemSupervisor
from cli import main


class TestInputValidation:
    """Test metric value validation."""

    def test_nan_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("nan"))

    def test_inf_primary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=float("inf"))

    def test_neg_inf_secondary_metric_rejected(self):
        with pytest.raises(ValueError, match="finite"):
            SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0, secondary_metric=float("-inf"))

    def test_valid_finite_metrics_accepted(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=10.0, secondary_metric=5.5)
        assert p.primary_metric == 10.0
        assert p.secondary_metric == 5.5

    def test_zero_metrics_accepted(self):
        p = SystemTaskPayload(task_id="T1", target_identifier="K1", primary_metric=0.0, secondary_metric=0.0)
        assert p.primary_metric == 0.0


class TestPHIGuard:
    """Test PHI detection and redaction."""

    def test_mrn_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Patient MRN-12345678")

    def test_ssn_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN: 123-45-6789")

    def test_phone_detected(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Call 555-123-4567")

    def test_clean_text_passes(self):
        PHIGuard.assert_no_phi("Specimen KEY-001 nominal")

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient MRN-12345678 status nominal")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN-" not in result

    def test_empty_text_passes(self):
        PHIGuard.assert_no_phi("")

    def test_none_safe(self):
        PHIGuard.assert_no_phi(None)


class TestAuditTrailSecurity:
    """Test audit trail security features."""

    def test_missing_secret_key_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            trail = AuditTrail(secret_key=None)
            # Clear any env var that might be set
            original = os.environ.pop("AUDIT_SECRET_KEY", None)
            try:
                with warnings.catch_warnings(record=True) as w:
                    warnings.simplefilter("always")
                    trail = AuditTrail(secret_key=None)
                    assert len(w) == 1
                    assert "AUDIT_SECRET_KEY not set" in str(w[0].message)
            finally:
                if original is not None:
                    os.environ["AUDIT_SECRET_KEY"] = original

    def test_explicit_key_used(self):
        trail = AuditTrail(secret_key="test-key-12345")
        entry = trail.log("test", "tier", "EVENT", {"data": "value"})
        assert "current_hash" in entry
        assert len(entry["current_hash"]) == 64  # SHA-256 hex

    def test_tamper_detection(self):
        trail = AuditTrail(secret_key="test-key")
        trail.log("actor", "tier", "EVENT1", {"data": "a"})
        trail.log("actor", "tier", "EVENT2", {"data": "b"})
        assert trail.verify_integrity() is True

        # Tamper with a log entry
        trail.logs[0]["payload_hash"] = "tampered"
        assert trail.verify_integrity() is False


class TestCLIErrorHandling:
    """Test CLI error handling."""

    def test_batch_missing_file(self):
        result = main(["batch", "-i", "nonexistent_file_xyz.csv"])
        assert result == 1

    def test_verify_audit_command(self):
        result = main(["verify-audit"])
        assert result == 0

    def test_batch_with_valid_csv(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-01,KEY-01,10.0,5.0,False,NOMINAL\n")
        output_file = tmp_path / "output.csv"
        result = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()

    def test_batch_skips_invalid_rows(self, tmp_path):
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("task_id,target_identifier,primary_metric,secondary_metric,is_critical_flag,status_descriptor\nTASK-01,KEY-01,10.0,5.0,False,NOMINAL\nTASK-02,KEY-02,invalid,5.0,False,NOMINAL\n")
        output_file = tmp_path / "output.csv"
        result = main(["batch", "-i", str(csv_file), "-o", str(output_file)])
        assert result == 0
        assert output_file.exists()
