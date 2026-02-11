"""
LLM Client wrapper for multiple providers
"""
import json
import time
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings, LLMProvider
from utils.logger import get_logger
from google import genai

import os


logger = get_logger(__name__)

class LLMClient:
    """Unified LLM client supporting multiple providers"""
    
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client"""
        if self.provider == LLMProvider.OPENAI:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.model = settings.OPENAI_MODEL
            self.temperature = settings.OPENAI_TEMPERATURE
            self.max_tokens = settings.OPENAI_MAX_TOKENS
            
        elif self.provider == LLMProvider.ANTHROPIC:
            from anthropic import Anthropic
            self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            self.model = settings.ANTHROPIC_MODEL
            self.temperature = 0.3
            self.max_tokens = 2000
            

        elif self.provider == LLMProvider.GEMINI:
            # Configure Gemini client
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            self.model = settings.GEMINI_MODEL
            self.temperature = 0.3
            self.max_tokens = 2000
        
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")
        
        logger.info(f"Initialized {self.provider} client with model {self.model}")
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    def complete(self, system_prompt: str, user_prompt: str, 
                 temperature: Optional[float] = None) -> str:
        """
        Get completion from LLM
        
        Args:
            system_prompt: System/role instruction
            user_prompt: User message
            temperature: Override default temperature
            
        Returns:
            LLM response text
        """
        temp = temperature if temperature is not None else self.temperature
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=temp,
                    max_tokens=self.max_tokens
                )
                return response.choices[0].message.content.strip()
            
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=temp,
                    max_tokens=self.max_tokens
                )
                return response.content[0].text.strip()
            
            elif self.provider == LLMProvider.GEMINI:
                # New GenAI SDK usage
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=user_prompt if system_prompt == "" else f"{system_prompt}\n\n{user_prompt}",
                    config=genai.types.GenerateContentConfig(
                        temperature=temp,
                        max_output_tokens=self.max_tokens,
                    ),
                )
                return response.text.strip()
            
        except Exception as e:
            logger.error(f"LLM completion error: {e}")
            raise
    
    def complete_json(self, system_prompt: str, user_prompt: str,
                     temperature: Optional[float] = None) -> Dict[str, Any]:
        """
        Get JSON completion from LLM
        
        Args:
            system_prompt: System/role instruction
            user_prompt: User message (should request JSON output)
            temperature: Override default temperature
            
        Returns:
            Parsed JSON dict
        """
        response_text = self.complete(system_prompt, user_prompt, temperature)
        
        # Extract JSON from response (handle markdown code blocks)
        response_text = response_text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        try:
            return json.loads(response_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response text: {response_text}")
            raise ValueError(f"LLM did not return valid JSON: {e}")
    
    def complete_multiple(self, system_prompt: str, user_prompt: str,
                         n: int = 3, temperature: Optional[float] = None) -> List[str]:
        """
        Get multiple completions (for inner council)
        
        Args:
            system_prompt: System/role instruction
            user_prompt: User message
            n: Number of completions
            temperature: Override default temperature
            
        Returns:
            List of response texts
        """
        responses = []
        for i in range(n):
            logger.debug(f"Inner council call {i+1}/{n}")
            response = self.complete(system_prompt, user_prompt, temperature)
            responses.append(response)
            time.sleep(0.5)  # Rate limiting
        return responses
    
    def complete_json_multiple(self, system_prompt: str, user_prompt: str,
                              n: int = 3, temperature: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Get multiple JSON completions (for inner council)
        
        Args:
            system_prompt: System/role instruction
            user_prompt: User message
            n: Number of completions
            temperature: Override default temperature
            
        Returns:
            List of parsed JSON dicts
        """
        responses = []
        for i in range(n):
            logger.debug(f"Inner council JSON call {i+1}/{n}")
            try:
                response = self.complete_json(system_prompt, user_prompt, temperature)
                responses.append(response)
            except Exception as e:
                logger.warning(f"Failed to get valid JSON on attempt {i+1}: {e}")
            time.sleep(0.5)  # Rate limiting
        
        if not responses:
            raise ValueError("All inner council attempts failed to produce valid JSON")
        
        return responses
