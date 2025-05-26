from abc import ABC, abstractmethod

'''Abstract agent runner class to be implemented for each LLM type'''
class AgentRunner(ABC):
  @abstractmethod
  def getResponse(self, query_string: str) -> str:
    pass
