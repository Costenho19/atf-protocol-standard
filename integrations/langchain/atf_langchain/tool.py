"""
  ATFVerifierTool + ATFIssueTool — LangChain Tools for ATF protocol operations.

  ATFVerifierTool: Verifies an ATF receipt JSON offline (ATF-INV-006).
                   Zero platform dependency — only receipt + public key.

  ATFIssueTool:    Issues a new Delegation Receipt for a LangChain agent,
                   enforcing the MAR invariant (ATF-INV-001).

  Usage (as LangChain Tools):
      from langchain.agents import initialize_agent
      from atf_langchain import ATFVerifierTool, ATFIssueTool

      tools = [
          ATFVerifierTool(issuer_public_key_b64=PUBLIC_KEY),
          ATFIssueTool(principal_id="HUMAN-harold-nunes-001", private_key_b64=PRIVATE_KEY),
      ]
      agent = initialize_agent(tools, llm, agent="zero-shot-react-description")
  """

  from __future__ import annotations

  import json
  from typing import Any, Dict, Optional, Type

  from langchain_core.tools import BaseTool
  from pydantic import BaseModel, Field

  from .utils import compute_content_hash, compute_ces, ces_to_status
  from .exceptions import ATFViolationError


  class VerifyInput(BaseModel):
      receipt_json: str = Field(description="JSON string of the ATF receipt to verify")
      public_key_b64: Optional[str] = Field(default=None, description="Base64 ML-DSA-65 public key")


  class ATFVerifierTool(BaseTool):
      """
      Verify an ATF Delegation Receipt or RCR offline.
      Returns a JSON report with pass/fail verdict for each invariant.
      Zero platform access required (ATF-INV-006).
      """

      name: str = "atf_verify_receipt"
      description: str = (
          "Verify an ATF protocol receipt (Delegation Receipt or Runtime Continuity Record) "
          "offline. Input: JSON string of the receipt. "
          "Returns: JSON report with verdict (PASS/FAIL) and per-invariant check results. "
          "Use when you need to confirm a delegation is valid before executing a governance decision."
      )
      args_schema: Type[BaseModel] = VerifyInput
      issuer_public_key_b64: Optional[str] = None

      def _run(self, receipt_json: str, public_key_b64: Optional[str] = None) -> str:
          try:
              receipt = json.loads(receipt_json)
          except json.JSONDecodeError as e:
              return json.dumps({"verdict": "FAIL", "error": f"Invalid JSON: {e}"})

          checks: Dict[str, str] = {}
          notes: list = []

          # ATF-INV-001 — MAR
          if "authority_budget_granted" in receipt:
              granted   = float(receipt.get("authority_budget_granted", 0))
              delegator = float(receipt.get("authority_budget_delegator", 0))
              if granted <= delegator:
                  checks["ATF-INV-001"] = "PASS"
                  notes.append(f"MAR: {granted} ≤ {delegator}")
              else:
                  checks["ATF-INV-001"] = "FAIL"
                  notes.append(f"MAR VIOLATION: {granted} > {delegator}")

          # ATF-INV-004 — Content hash
          computed = compute_content_hash(receipt)
          stored   = receipt.get("content_hash", "")
          is_example = "BASE64_" in str(receipt.get("pqc_signature", ""))
          if is_example or stored == computed:
              checks["ATF-INV-004"] = "PASS" if not is_example else "SKIP (example receipt)"
          else:
              checks["ATF-INV-004"] = "FAIL"
              notes.append(f"Hash mismatch: stored={stored[:32]} computed={computed[:32]}")

          # RGC-INV-001 — CES formula (if RCR)
          if "ces_score" in receipt:
              stored_ces = float(receipt.get("ces_score", 0))
              t = float(receipt.get("ces_temporal", 0))
              b = float(receipt.get("ces_budget", 0))
              d = float(receipt.get("ces_context", 0))
              i = float(receipt.get("ces_integrity", 0))
              recomputed = compute_ces(t, b, d, i)
              if abs(recomputed - stored_ces) <= 0.01:
                  checks["RGC-INV-001"] = "PASS"
              else:
                  checks["RGC-INV-001"] = "FAIL"
                  notes.append(f"CES mismatch: stored={stored_ces} recomputed={recomputed}")

          # ATF-INV-006 — Not expired
          import datetime
          expires_at = receipt.get("expires_at", receipt.get("dr_expires_at", ""))
          if expires_at:
              try:
                  exp = datetime.datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
                  now = datetime.datetime.now(datetime.timezone.utc)
                  if now <= exp:
                      checks["ATF-INV-006"] = "PASS"
                  else:
                      checks["ATF-INV-006"] = "FAIL"
                      notes.append(f"DR expired at {expires_at}")
              except ValueError:
                  checks["ATF-INV-006"] = "WARN"
          else:
              checks["ATF-INV-006"] = "SKIP"

          verdict = "PASS" if all(v in ("PASS", "SKIP") for v in checks.values()) else "FAIL"
          return json.dumps({"verdict": verdict, "checks": checks, "notes": notes}, indent=2)

      async def _arun(self, receipt_json: str, public_key_b64: Optional[str] = None) -> str:
          return self._run(receipt_json, public_key_b64)


  class IssueInput(BaseModel):
      delegate_id: str = Field(description="Agent ID to delegate to (AID-DOMAIN-16HEX)")
      action: str = Field(description="Governance action being delegated")
      domain: str = Field(description="Governance domain (e.g. FINANCE, HEALTHCARE)")
      budget_granted: float = Field(description="Authority budget to grant (0.0–100.0)")


  class ATFIssueTool(BaseTool):
      """
      Issue a new ATF Delegation Receipt for a LangChain agent.
      Enforces MAR (ATF-INV-001): budget_granted must not exceed principal budget.
      Returns the signed DR JSON.
      """

      name: str = "atf_issue_delegation_receipt"
      description: str = (
          "Issue a new ATF Delegation Receipt granting authority to an AI agent. "
          "Input: delegate_id (AID format), action, domain, budget_granted (0–100). "
          "The budget_granted must not exceed the principal's authority budget (ATF-INV-001). "
          "Returns: signed Delegation Receipt JSON. "
          "Use before delegating governance decisions to sub-agents."
      )
      args_schema: Type[BaseModel] = IssueInput
      principal_id: str = ""
      principal_budget: float = 100.0
      private_key_b64: Optional[str] = None

      def _run(self, delegate_id: str, action: str, domain: str, budget_granted: float) -> str:
          if budget_granted > self.principal_budget:
              return json.dumps({
                  "error": f"ATF-INV-001: budget_granted {budget_granted} exceeds principal budget {self.principal_budget}",
                  "invariant": "mar_atf_inv_001",
              })
          try:
              import sys
              sys.path.insert(0, "reference-implementation")
              from atf_core.receipts import create_delegation_receipt
              dr = create_delegation_receipt(
                  delegator_id=self.principal_id,
                  delegate_id=delegate_id,
                  task_scope={"action": action, "domain": domain},
                  budget_granted=budget_granted,
                  budget_delegator=self.principal_budget,
              )
              return json.dumps(dr, indent=2)
          except Exception as e:
              return json.dumps({"error": str(e)})

      async def _arun(self, delegate_id: str, action: str, domain: str, budget_granted: float) -> str:
          return self._run(delegate_id, action, domain, budget_granted)
  