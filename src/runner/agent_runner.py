from abc import ABC, abstractmethod

'''Abstract agent runner class to be implemented for each LLM type'''
class AgentRunner(ABC):
  @abstractmethod
  def getResponseAsync(self, query_string: str):
    pass

  @abstractmethod
  def getResponse(self, query_string: str):
    pass
