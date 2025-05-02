from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """
    Abstract base class for Large Language Model providers.
    """

    @abstractmethod
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generates an answer based on the provided query and context.

        Args:
            query: The user's original query.
            context: The context retrieved from relevant document chunks.

        Returns:
            A string containing the generated answer.
        """
        pass
