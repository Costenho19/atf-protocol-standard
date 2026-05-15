"""
  ATF Receipt Creation — RFC-ATF-1 §5, RFC-ATF-2 §5
  Enforces protocol invariants at creation time.
  """

  import hashlib
  import json
  import secrets
  import time
  from datetime import datetime, timezone, timedelta
  from typing import Any, Dict, Optional


  def _new_id(prefix: str) -> str:
      return f"{prefix}-{secrets.token_hex(8).upper()}"


  _HASH_EXCLUDE = {"content_hash", "pqc_signature", "pqc_algorithm", "_comment", "_ces_formula"}


  def compute_content_hash(receipt: Dict[str, Any]) -> str:
      payload = {k: v for k, v in receipt.items() if k not in _HASH_EXCLUDE}
      canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
      digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
      return f"sha256:{digest}"


  def compute_ces(temporal: float, budget: float, context: float, integrity: float) -> float:
      """CES = T*0.30 + B*0.30 + D*0.20 + I*0.20  (RGC-INV-002)."""
      return round(temporal * 0.30 + budget * 0.30 + context * 0.20 + integrity * 0.20, 2)


  def ces_to_status(ces: float) -> str:
      """Map CES score to continuity status (RGC-INV-003)."""
      if ces >= 75.0:
          return "NOMINAL"
      elif ces >= 50.0:
          return "MONITORING"
      elif ces >= 30.0:
          return "WARNING"
      elif ces >= 10.0:
          return "CRITICAL"
      return "HALT"


  def create_delegation_receipt(
      *,
      delegator_id: str,
      delegate_id: str,
      task_scope: Dict[str, Any],
      budget_granted: float,
      budget_delegator: float,
      parent_delegation_id: Optional[str] = None,
      chain_root_id: Optional[str] = None,
      delegation_depth: int = 0,
      expires_in_seconds: Optional[int] = 86400,
      delegator_public_key: str = "",
      metadata: Optional[Dict] = None,
  ) -> Dict[str, Any]:
      """
      Create a Delegation Receipt (DR) per RFC-ATF-1 §5.

      Enforces ATF-INV-001 (MAR): budget_granted MUST NOT exceed budget_delegator.
      """
      if budget_granted > budget_delegator:
          raise ValueError(
              f"ATF-INV-001 (MAR) VIOLATED: budget_granted ({budget_granted}) "
              f"must not exceed budget_delegator ({budget_delegator})"
          )
      if not 0.0 <= budget_granted <= 100.0:
          raise ValueError(f"budget_granted must be in [0.0, 100.0], got {budget_granted}")

      delegation_id = _new_id("ATFDR")
      now = datetime.now(timezone.utc)
      if chain_root_id is None:
          chain_root_id = delegation_id  # ATF-INV-003

      receipt: Dict[str, Any] = {
          "delegation_id": delegation_id,
          "delegator_id": delegator_id,
          "delegate_id": delegate_id,
          "task_scope": task_scope,
          "authority_budget_delegator": budget_delegator,
          "authority_budget_granted": budget_granted,
          "parent_delegation_id": parent_delegation_id,
          "chain_root_id": chain_root_id,
          "delegation_depth": delegation_depth,
          "delegator_public_key": delegator_public_key,
          "pqc_algorithm": "dilithium3",
          "expires_at": (now + timedelta(seconds=expires_in_seconds)).isoformat()
                        if expires_in_seconds else None,
          "status": "ACTIVE",
          "created_at": now.isoformat(),
          "metadata": metadata or {},
      }
      receipt["content_hash"] = compute_content_hash(receipt)
      receipt["pqc_signature"] = ""
      return receipt


  def create_runtime_continuity_record(
      *,
      tar_id: str,
      delegation_id: str,
      agent_id: str,
      chain_root_id: str,
      ces_temporal: float,
      ces_budget: float,
      ces_context: float,
      ces_integrity: float,
      budget_at_admission: float,
      budget_remaining: float,
      context_drift_pct: float,
      sample_reason: str = "SCHEDULED",
      active_anomalies: int = 0,
      fragmentation_score: float = 0.0,
      predecessor_rcr_id: Optional[str] = None,
      escalation_event_id: Optional[str] = None,
      reauth_challenge_id: Optional[str] = None,
      dr_expires_at: Optional[str] = None,
  ) -> Dict[str, Any]:
      """
      Create a Runtime Continuity Record (RCR) per RFC-ATF-2 §5.

      Enforces RGC-INV-001 (tar_id not null), RGC-INV-002 (CES formula),
      and RGC-INV-003 (status thresholds).
      """
      if not tar_id:
          raise ValueError("RGC-INV-001 VIOLATED: tar_id must not be null")

      valid_reasons = {"SCHEDULED", "EVENT_DRIVEN", "MANUAL", "EXECUTION_COMPLETE", "HALT"}
      if sample_reason not in valid_reasons:
          raise ValueError(f"sample_reason must be one of {valid_reasons}")

      ces_score = compute_ces(ces_temporal, ces_budget, ces_context, ces_integrity)
      continuity_status = ces_to_status(ces_score)

      now_ns = time.time_ns()
      now_ts = datetime.now(timezone.utc).isoformat()

      receipt: Dict[str, Any] = {
          "rcr_id": _new_id("ATFRCR"),
          "tar_id": tar_id,
          "delegation_id": delegation_id,
          "agent_id": agent_id,
          "chain_root_id": chain_root_id,
          "execution_ns": now_ns,
          "execution_ts": now_ts,
          "ces_score": ces_score,
          "ces_temporal": ces_temporal,
          "ces_budget": ces_budget,
          "ces_context": ces_context,
          "ces_integrity": ces_integrity,
          "continuity_status": continuity_status,
          "predecessor_rcr_id": predecessor_rcr_id,
          "budget_at_admission": budget_at_admission,
          "budget_remaining": budget_remaining,
          "context_drift_pct": context_drift_pct,
          "active_anomalies": active_anomalies,
          "dr_expires_at": dr_expires_at,
          "fragmentation_score": fragmentation_score,
          "escalation_event_id": escalation_event_id,
          "reauth_challenge_id": reauth_challenge_id,
          "sample_reason": sample_reason,
          "pqc_algorithm": "dilithium3",
          "_ces_formula": (
              f"CES = T({ces_temporal})x0.30 + B({ces_budget})x0.30 + "
              f"D({ces_context})x0.20 + I({ces_integrity})x0.20 = {ces_score} - {continuity_status}"
          ),
      }
      receipt["content_hash"] = compute_content_hash(receipt)
      receipt["pqc_signature"] = ""
      return receipt
  