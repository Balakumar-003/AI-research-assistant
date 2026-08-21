import logging
from typing import List, Dict, Any, AsyncGenerator, Tuple
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.client = None
        
        if self.provider == "openai":
            import openai
            self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            logger.warning(f"LLM Provider {self.provider} not fully supported yet.")

    async def generate(self, messages: List[Dict[str, str]]) -> Tuple[str, Dict[str, int]]:
        """
        Generates a non-streaming response.
        Returns (response_text, usage_dict)
        """
        if self.provider == "openai":
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                )
                
                content = response.choices[0].message.content
                usage = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens
                }
                return content, usage
                
            except Exception as e:
                logger.error(f"OpenAI error: {str(e)}")
                raise e
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")

    async def generate_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        Generates a streaming response.
        """
        if self.provider == "openai":
            try:
                stream = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    stream=True
                )
                
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            except Exception as e:
                logger.error(f"OpenAI stream error: {str(e)}")
                raise e
        else:
            raise NotImplementedError(f"Provider {self.provider} not implemented")

llm_service = LLMService()
