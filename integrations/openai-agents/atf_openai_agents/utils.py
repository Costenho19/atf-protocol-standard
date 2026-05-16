"""Shared utilities for atf-openai-agents."""
  import hashlib, json
  from typing import Any, Dict

  _HASH_EXCLUDE = {"content_hash","pqc_signature","pqc_algorithm","_comment","_ces_formula","_test_note"}

  def compute_content_hash(receipt:Dict[str,Any])->str:
      payload = {k:v for k,v in receipt.items() if k not in _HASH_EXCLUDE}
      canonical = json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=False)
      return "sha256:"+hashlib.sha256(canonical.encode()).hexdigest()

  def compute_ces(t:float,b:float,d:float,i:float)->float:
      return round(t*0.30+b*0.30+d*0.20+i*0.20,2)

  def ces_to_status(ces:float)->str:
      if   ces>=75.0: return "NOMINAL"
      elif ces>=50.0: return "MONITORING"
      elif ces>=30.0: return "WARNING"
      elif ces>=10.0: return "CRITICAL"
      return "HALT"
  