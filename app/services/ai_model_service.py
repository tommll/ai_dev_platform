import asyncio
import time
import httpx
from typing import Dict, Any, Optional
from app.config import settings
import pdb

class AIModelService:
    """Service for calling different AI model providers"""
    
    def __init__(self):
        self.openai_api_key = settings.openai_api_key if hasattr(settings, 'openai_api_key') else None
        self.anthropic_api_key = settings.anthropic_api_key if hasattr(settings, 'anthropic_api_key') else None
    
    async def call_model(self, prompt_config: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Call AI model with the given configuration"""
        provider = prompt_config.get("provider", "openai")
        model = prompt_config.get("model", "gpt-3.5-turbo")
        
        # Format the prompt using the template
        template = prompt_config.get("template", "{input}")
        # formatted_prompt = template.format(**input_data)
        formatted_prompt = template.format(input=input_data)
        
        start_time = time.time()
        
        try:
            if provider == "openai":
                result = await self._call_openai(model, formatted_prompt, prompt_config)
            elif provider == "anthropic":
                result = await self._call_anthropic(model, formatted_prompt, prompt_config)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            execution_time = time.time() - start_time
            
            return {
                "output": result["output"],
                "execution_time_ms": execution_time * 1000,
                "cost_usd": result.get("cost_usd", 0.0),
                "tokens_used": result.get("tokens_used", 0),
                "model": model,
                "provider": provider
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "output": None,
                "error": str(e),
                "execution_time_ms": execution_time * 1000,
                "cost_usd": 0.0,
                "tokens_used": 0,
                "model": model,
                "provider": provider
            }
    
    async def _call_openai(self, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call OpenAI API"""
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not configured")
        
        temperature = config.get("temperature", 0.7)
        max_tokens = config.get("max_tokens", 1000)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.openai_api_key}"},
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"OpenAI API error: {response.status_code} - {response.text}")
            
            result = response.json()
            output = result["choices"][0]["message"]["content"]
            
            # Estimate cost (rough calculation)
            tokens_used = result["usage"]["total_tokens"]
            cost_usd = self._estimate_openai_cost(model, tokens_used)
            
            return {
                "output": output,
                "tokens_used": tokens_used,
                "cost_usd": cost_usd
            }
    
    async def _call_anthropic(self, model: str, prompt: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Call Anthropic API"""
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")
        
        max_tokens = config.get("max_tokens", 1000)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.anthropic_api_key,
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": model,
                    "max_tokens": max_tokens,
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=30.0
            )
            
            if response.status_code != 200:
                raise Exception(f"Anthropic API error: {response.status_code} - {response.text}")
            
            result = response.json()
            output = result["content"][0]["text"]
            
            # Estimate cost (rough calculation)
            tokens_used = result["usage"]["input_tokens"] + result["usage"]["output_tokens"]
            cost_usd = self._estimate_anthropic_cost(model, tokens_used)
            
            return {
                "output": output,
                "tokens_used": tokens_used,
                "cost_usd": cost_usd
            }
    
    def _estimate_openai_cost(self, model: str, tokens: int) -> float:
        """Estimate OpenAI cost based on model and tokens"""
        # Rough cost estimates per 1K tokens (you should update these regularly)
        costs = {
            "gpt-4": 0.03,  # $0.03 per 1K input tokens
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.002,
            "gpt-3.5-turbo-16k": 0.003
        }
        
        base_cost = costs.get(model, 0.002)  # Default to gpt-3.5-turbo cost
        return (tokens / 1000) * base_cost
    
    def _estimate_anthropic_cost(self, model: str, tokens: int) -> float:
        """Estimate Anthropic cost based on model and tokens"""
        # Rough cost estimates per 1K tokens
        costs = {
            "claude-3-opus-20240229": 0.015,
            "claude-3-sonnet-20240229": 0.003,
            "claude-3-haiku-20240307": 0.00025
        }
        
        base_cost = costs.get(model, 0.003)  # Default to claude-3-sonnet cost
        return (tokens / 1000) * base_cost 