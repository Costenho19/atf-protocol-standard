"""ATF HTTP exceptions."""
  from fastapi import HTTPException

  class ATFHTTPException(HTTPException):
      def __init__(self, status_code:int, reason:str, message:str):
          super().__init__(status_code=status_code, detail={"error":message,"atf_reason":reason,"protocol":"RFC-ATF-1/RFC-ATF-2"})
          self.atf_reason = reason

  class ATFHaltHTTPException(ATFHTTPException):
      def __init__(self, ces_score:float, delegation_id:str=""):
          super().__init__(503,"rgc_inv_003_halt",f"RGC-INV-003: CES={ces_score:.1f} < 10.0 — HALT. Reauthorization required.")
          self.ces_score = ces_score
          self.delegation_id = delegation_id
  