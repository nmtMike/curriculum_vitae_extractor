import uuid
from typing import List, Optional
from ..helper.logger import Logger
from ..client.llm_client import OpenAIClient
# from ..client.document_intelligence_client import AzDocumentIntelligenceClient

class BaseAgent:
    """
    Base Agent class to improve the conversational experience
    """

    def __init__(
        self,
        description: str = None,
    ):
        self.last_prompt = None
        self.last_prompt_id = None
        self.last_result = None
        self.agent_info = description

        # Instantiate the logger
        self.logger = Logger()
        self.llm = OpenAIClient.create_azure_openai_chat_client()
        # self.document_inteligence = AzDocumentIntelligenceClient.create_document_intelligence_client()


    def add_skills(self):
        pass

    def call_llm_with_prompt(self):
        pass

    def chat(self, query: str, output_type: Optional[str] = None):
        pass

    def generate_code(self, query: str, output_type: Optional[str] = None):
        pass

    def execute_code(self):
        pass

    def train(self) -> None:
        pass

    def clear_memory(self):
        pass

    def add_message(self):
        pass

    def check_malicious_keywords_in_query(self, query):
        dangerous_modules = [
            " os",
            " io",
            ".os",
            ".io",
            "'os'",
            "'io'",
            '"os"',
            '"io"',
            "chr(",
            "chr)",
            "chr ",
            "(chr",
            "b64decode",
        ]
        return any(module in query for module in dangerous_modules)

    def assign_prompt_id(self):
        """Assign a prompt ID"""

        self.last_prompt_id = uuid.uuid4()

        if self.logger:
            self.logger.log(f"Prompt ID: {self.last_prompt_id}")

    def clarification_questions(self, query: str) -> List[str]:
        pass

    def start_new_conversation(self):
        """
        Clears the previous conversation
        """
        self.clear_memory()

    def explain(self) -> str:
        pass

    def rephrase_query(self, query: str):
        pass

    @property
    def logs(self):
        return self.logger.logs

    @property
    def last_error(self):
        raise NotImplementedError

    @property
    def last_query_log_id(self):
        raise NotImplementedError
