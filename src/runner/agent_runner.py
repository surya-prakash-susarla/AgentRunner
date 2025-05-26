from abc import ABC, abstractmethod


class AgentRunner(ABC):
  @abstractmethod
  def getResponse(self, query_string: str) -> str:
    pass
