"""ATF utility functions shared across the LangChain integration."""
  import hashlib
  import json
  from typing import Any, Dict

  _HASH_EXCLUDE = {"content_hash", "pqc_signature", "pqc_algorithm", "_comment", "_ces_formula", "_test_note"}

  def compute_content_hash(receipt: Dict[str, Any]) -> str:
      """Recompute ATF content hash (ATF-INV-004, FVP-INV-007)."""
      payload = {k: v for k, v in receipt.items() if k not in _HASH_EXCLUDE}
      canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
      return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()

  def compute_ces(temporal: float, budget: float, context: float, integrity: float) -> float:
      """CES = T×0.30 + B×0.30 + D×0.20 + I×0.20 (RGC-INV-001 — immutable formula)."""
      return round(temporal * 0.30 + budget * 0.30 + context * 0.20 + integrity * 0.20, 2)

  def ces_to_status(ces: float) -> str:
      """Map CES score to continuity status (RGC-INV-003 thresholds — not configurable)."""
      if   ces >= 75.0: return "NOMINAL"
      elif ces >= 50.0: return "MONITORING"
      elif ces >= 30.0: return "WARNING"
      elif ces >= 10.0: return "CRITICAL"
      return "HALT"
  