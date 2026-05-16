"""ATF exceptions for openai-agents integration."""
  from typing import Optional

  class ATFError(Exception):
      def __init__(self, message:str, *, reason:str="", delegation_id:Optional[str]=None):
          super().__init__(message)
          self.reason = reason
          self.delegation_id = delegation_id

  class ATFHaltError(ATFError):
      def __init__(self, message:str, *, ces_score:float, delegation_id:Optional[str]=None):
          super().__init__(message, reason="rgc_inv_003_halt", delegation_id=delegation_id)
          self.ces_score = ces_score

  class ATFViolationError(ATFError):
      pass
  