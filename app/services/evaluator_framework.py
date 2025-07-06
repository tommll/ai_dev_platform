import asyncio
from typing import Dict, Any, Callable, Optional
import httpx
from sentence_transformers import SentenceTransformer
import numpy as np


class EvaluatorFramework:
    """Framework for custom and built-in evaluators"""

    def __init__(self):
        self.evaluators: Dict[str, Callable] = {}
        self._sentence_model = None
        self._register_builtin_evaluators()

    def _register_builtin_evaluators(self):
        """Register all built-in evaluators"""
        self.register_evaluator("exact_match", exact_match_evaluator)
        self.register_evaluator("semantic_similarity", semantic_similarity_evaluator)
        self.register_evaluator("llm_judge", llm_judge_evaluator)
        self.register_evaluator("latency", latency_evaluator)
        self.register_evaluator("cost", cost_evaluator)

    def register_evaluator(self, name: str, evaluator_func: Callable):
        """Register a custom evaluator function"""
        self.evaluators[name] = evaluator_func

    async def run_evaluator(self, evaluator_config: Dict[str, Any], 
                          input_data: Dict[str, Any], 
                          expected_output: str, 
                          actual_output: str,
                          execution_time_ms: Optional[float] = None,
                          cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Run an evaluator with the given configuration"""
        evaluator_name = evaluator_config["name"]
        
        if evaluator_name not in self.evaluators:
            return {
                "score": 0.0,
                "passed": False,
                "error": f"Evaluator '{evaluator_name}' not found"
            }

        evaluator_func = self.evaluators[evaluator_name]
        
        try:
            result = await evaluator_func(
                input_data=input_data,
                expected_output=expected_output,
                actual_output=actual_output,
                execution_time_ms=execution_time_ms,
                cost_usd=cost_usd,
                config=evaluator_config.get("config", {})
            )
            return result
        except Exception as e:
            return {
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }

    def _get_sentence_model(self):
        """Lazy load sentence transformer model"""
        if self._sentence_model is None:
            self._sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        return self._sentence_model


# Built-in evaluators
async def exact_match_evaluator(input_data: Dict[str, Any], 
                               expected_output: str, 
                               actual_output: str,
                               execution_time_ms: Optional[float] = None,
                               cost_usd: Optional[float] = None,
                               config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Exact string match evaluator"""
    config = config or {}
    case_sensitive = config.get("case_sensitive", False)
    
    if case_sensitive:
        is_match = actual_output.strip() == expected_output.strip()
    else:
        is_match = actual_output.strip().lower() == expected_output.strip().lower()
    
    return {
        "score": 1.0 if is_match else 0.0,
        "passed": is_match,
        "details": {
            "case_sensitive": case_sensitive,
            "expected": expected_output.strip(),
            "actual": actual_output.strip()
        }
    }


async def semantic_similarity_evaluator(input_data: Dict[str, Any], 
                                       expected_output: str, 
                                       actual_output: str,
                                       execution_time_ms: Optional[float] = None,
                                       cost_usd: Optional[float] = None,
                                       config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Semantic similarity evaluator using sentence transformers"""
    config = config or {}
    threshold = config.get("threshold", 0.8)
    
    try:
        # Get sentence transformer model
        framework = EvaluatorFramework()
        model = framework._get_sentence_model()
        
        # Compute embeddings
        embeddings = model.encode([expected_output, actual_output])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        return {
            "score": float(similarity),
            "passed": similarity >= threshold,
            "details": {
                "similarity": float(similarity),
                "threshold": threshold
            }
        }
    except Exception as e:
        return {
            "score": 0.0,
            "passed": False,
            "error": f"Semantic similarity computation failed: {str(e)}"
        }


async def llm_judge_evaluator(input_data: Dict[str, Any], 
                             expected_output: str, 
                             actual_output: str,
                             execution_time_ms: Optional[float] = None,
                             cost_usd: Optional[float] = None,
                             config: Dict[str, Any] = None) -> Dict[str, Any]:
    """LLM-based evaluator using a judge model"""
    config = config or {}
    judge_model = config.get("judge_model", "gpt-3.5-turbo")
    threshold = config.get("threshold", 0.7)
    api_key = config.get("api_key")
    
    if not api_key:
        return {
            "score": 0.0,
            "passed": False,
            "error": "API key required for LLM judge evaluator"
        }
    
    try:
        judge_prompt = f"""
        Evaluate the quality of this response on a scale of 0-1:

        Question/Input: {input_data}
        Expected Answer: {expected_output}
        Actual Answer: {actual_output}

        Consider:
        - Accuracy and correctness
        - Completeness of the response
        - Relevance to the question
        - Clarity and coherence

        Provide only a number between 0 and 1 as your response.
        """
        
        # Call judge model (example using OpenAI API)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": judge_model,
                    "messages": [{"role": "user", "content": judge_prompt}],
                    "temperature": 0.1,
                    "max_tokens": 10
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                score_text = result["choices"][0]["message"]["content"].strip()
                try:
                    score = float(score_text)
                    score = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                except ValueError:
                    score = 0.0
                
                return {
                    "score": score,
                    "passed": score >= threshold,
                    "details": {
                        "judge_model": judge_model,
                        "threshold": threshold,
                        "raw_response": score_text
                    }
                }
            else:
                return {
                    "score": 0.0,
                    "passed": False,
                    "error": f"API call failed: {response.status_code}"
                }
                
    except Exception as e:
        return {
            "score": 0.0,
            "passed": False,
            "error": f"LLM judge evaluation failed: {str(e)}"
        }


async def latency_evaluator(input_data: Dict[str, Any], 
                           expected_output: str, 
                           actual_output: str,
                           execution_time_ms: Optional[float] = None,
                           cost_usd: Optional[float] = None,
                           config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Latency evaluator"""
    config = config or {}
    max_latency_ms = config.get("max_latency_ms", 5000)  # 5 seconds default
    
    if execution_time_ms is None:
        return {
            "score": 0.0,
            "passed": False,
            "error": "Execution time not provided"
        }
    
    # Score based on latency (lower is better)
    if execution_time_ms <= max_latency_ms:
        score = 1.0 - (execution_time_ms / max_latency_ms) * 0.5  # 0.5 to 1.0
    else:
        score = 0.0
    
    return {
        "score": score,
        "passed": execution_time_ms <= max_latency_ms,
        "details": {
            "execution_time_ms": execution_time_ms,
            "max_latency_ms": max_latency_ms
        }
    }


async def cost_evaluator(input_data: Dict[str, Any], 
                        expected_output: str, 
                        actual_output: str,
                        execution_time_ms: Optional[float] = None,
                        cost_usd: Optional[float] = None,
                        config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Cost evaluator"""
    config = config or {}
    max_cost_usd = config.get("max_cost_usd", 0.10)  # 10 cents default
    
    if cost_usd is None:
        return {
            "score": 0.0,
            "passed": False,
            "error": "Cost not provided"
        }
    
    # Score based on cost (lower is better)
    if cost_usd <= max_cost_usd:
        score = 1.0 - (cost_usd / max_cost_usd) * 0.5  # 0.5 to 1.0
    else:
        score = 0.0
    
    return {
        "score": score,
        "passed": cost_usd <= max_cost_usd,
        "details": {
            "cost_usd": cost_usd,
            "max_cost_usd": max_cost_usd
        }
    } 