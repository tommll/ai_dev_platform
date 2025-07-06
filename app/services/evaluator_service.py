from typing import Dict, Any, List, Optional, Callable, Type
from abc import ABC, abstractmethod
import asyncio
import logging
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class BaseEvaluator(ABC):
    """Base class for all evaluators"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def evaluate(self, expected_output: str, actual_output: str, 
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate the actual output against expected output"""
        pass
    
    def validate_config(self) -> bool:
        """Validate evaluator configuration"""
        return True


class ExactMatchEvaluator(BaseEvaluator):
    """Exact string match evaluator"""
    
    def validate_config(self) -> bool:
        required_fields = []
        for field in required_fields:
            if field not in self.config:
                logger.error(f"Missing required field '{field}' in ExactMatchEvaluator config")
                return False
        return True
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate exact string match"""
        try:
            case_sensitive = self.config.get("case_sensitive", False)
            strip_whitespace = self.config.get("strip_whitespace", True)
            
            if strip_whitespace:
                expected = expected_output.strip()
                actual = actual_output.strip()
            else:
                expected = expected_output
                actual = actual_output
            
            if not case_sensitive:
                expected = expected.lower()
                actual = actual.lower()
            
            is_match = actual == expected
            score = 1.0 if is_match else 0.0
            
            return {
                "evaluator_type": "exact_match",
                "score": score,
                "passed": is_match,
                "details": {
                    "case_sensitive": case_sensitive,
                    "strip_whitespace": strip_whitespace,
                    "expected": expected_output.strip(),
                    "actual": actual_output.strip(),
                    "matched": is_match
                }
            }
        except Exception as e:
            logger.error(f"ExactMatchEvaluator error: {e}")
            return {
                "evaluator_type": "exact_match",
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


class SemanticSimilarityEvaluator(BaseEvaluator):
    """Semantic similarity evaluator using sentence transformers"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._model = None
    
    def validate_config(self) -> bool:
        threshold = self.config.get("threshold")
        if threshold is None or not isinstance(threshold, (int, float)):
            logger.error("SemanticSimilarityEvaluator requires 'threshold' config")
            return False
        if not 0 <= threshold <= 1:
            logger.error("SemanticSimilarityEvaluator threshold must be between 0 and 1")
            return False
        return True
    
    def _get_model(self):
        """Lazy load sentence transformer model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                raise ImportError("sentence-transformers not installed. Install with: pip install sentence-transformers")
        return self._model
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate semantic similarity"""
        try:
            threshold = self.config.get("threshold", 0.8)
            
            # Get model and compute embeddings
            model = self._get_model()
            embeddings = model.encode([expected_output, actual_output])
            
            # Calculate cosine similarity
            import numpy as np
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            score = float(similarity)
            passed = score >= threshold
            
            return {
                "evaluator_type": "semantic_similarity",
                "score": score,
                "passed": passed,
                "details": {
                    "similarity": score,
                    "threshold": threshold,
                    "expected": expected_output,
                    "actual": actual_output
                }
            }
        except Exception as e:
            logger.error(f"SemanticSimilarityEvaluator error: {e}")
            return {
                "evaluator_type": "semantic_similarity",
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


class LatencyEvaluator(BaseEvaluator):
    """Latency evaluator"""
    
    def validate_config(self) -> bool:
        max_latency = self.config.get("max_latency_ms")
        if max_latency is None or not isinstance(max_latency, (int, float)):
            logger.error("LatencyEvaluator requires 'max_latency_ms' config")
            return False
        if max_latency <= 0:
            logger.error("LatencyEvaluator max_latency_ms must be positive")
            return False
        return True
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate latency"""
        try:
            max_latency_ms = self.config.get("max_latency_ms", 5000)
            
            if execution_time_ms is None:
                return {
                    "evaluator_type": "latency",
                    "score": 0.0,
                    "passed": False,
                    "error": "Execution time not provided"
                }
            
            # Score based on latency (lower is better)
            if execution_time_ms <= max_latency_ms:
                score = 1.0 - (execution_time_ms / max_latency_ms) * 0.5  # 0.5 to 1.0
            else:
                score = 0.0
            
            passed = execution_time_ms <= max_latency_ms
            
            return {
                "evaluator_type": "latency",
                "score": score,
                "passed": passed,
                "details": {
                    "execution_time_ms": execution_time_ms,
                    "max_latency_ms": max_latency_ms,
                    "score": score
                }
            }
        except Exception as e:
            logger.error(f"LatencyEvaluator error: {e}")
            return {
                "evaluator_type": "latency",
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


class CostEvaluator(BaseEvaluator):
    """Cost evaluator"""
    
    def validate_config(self) -> bool:
        max_cost = self.config.get("max_cost_usd")
        if max_cost is None or not isinstance(max_cost, (int, float)):
            logger.error("CostEvaluator requires 'max_cost_usd' config")
            return False
        if max_cost <= 0:
            logger.error("CostEvaluator max_cost_usd must be positive")
            return False
        return True
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate cost"""
        try:
            max_cost_usd = self.config.get("max_cost_usd", 0.10)
            
            if cost_usd is None:
                return {
                    "evaluator_type": "cost",
                    "score": 0.0,
                    "passed": False,
                    "error": "Cost not provided"
                }
            
            # Score based on cost (lower is better)
            if cost_usd <= max_cost_usd:
                score = 1.0 - (cost_usd / max_cost_usd) * 0.5  # 0.5 to 1.0
            else:
                score = 0.0
            
            passed = cost_usd <= max_cost_usd
            
            return {
                "evaluator_type": "cost",
                "score": score,
                "passed": passed,
                "details": {
                    "cost_usd": cost_usd,
                    "max_cost_usd": max_cost_usd,
                    "score": score
                }
            }
        except Exception as e:
            logger.error(f"CostEvaluator error: {e}")
            return {
                "evaluator_type": "cost",
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


class LLMJudgeEvaluator(BaseEvaluator):
    """LLM-based evaluator using a judge model"""
    
    def validate_config(self) -> bool:
        required_fields = ["api_key", "judge_model"]
        for field in required_fields:
            if field not in self.config:
                logger.error(f"LLMJudgeEvaluator requires '{field}' config")
                return False
        return True
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate using LLM judge"""
        try:
            api_key = self.config.get("api_key")
            judge_model = self.config.get("judge_model", "gpt-3.5-turbo")
            threshold = self.config.get("threshold", 0.7)
            
            if not api_key:
                return {
                    "evaluator_type": "llm_judge",
                    "score": 0.0,
                    "passed": False,
                    "error": "API key required for LLM judge evaluator"
                }
            
            # Create judge prompt
            judge_prompt = f"""
            Evaluate the quality of this response on a scale of 0-1:

            Question/Input: {input_data or 'N/A'}
            Expected Answer: {expected_output}
            Actual Answer: {actual_output}

            Consider:
            - Accuracy and correctness
            - Completeness of the response
            - Relevance to the question
            - Clarity and coherence

            Provide only a number between 0 and 1 as your response.
            """
            
            # Call judge model
            import httpx
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
                    
                    passed = score >= threshold
                    
                    return {
                        "evaluator_type": "llm_judge",
                        "score": score,
                        "passed": passed,
                        "details": {
                            "judge_model": judge_model,
                            "threshold": threshold,
                            "raw_response": score_text,
                            "score": score
                        }
                    }
                else:
                    return {
                        "evaluator_type": "llm_judge",
                        "score": 0.0,
                        "passed": False,
                        "error": f"API call failed: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"LLMJudgeEvaluator error: {e}")
            return {
                "evaluator_type": "llm_judge",
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


class EvaluatorService:
    """Service for managing and creating evaluators"""
    
    def __init__(self):
        self._evaluators: Dict[str, Type[BaseEvaluator]] = {}
        self._custom_evaluators: Dict[str, Callable] = {}
        self._register_builtin_evaluators()
    
    def _register_builtin_evaluators(self):
        """Register all built-in evaluators"""
        self.register_evaluator("exact_match", ExactMatchEvaluator)
        self.register_evaluator("semantic_similarity", SemanticSimilarityEvaluator)
        self.register_evaluator("latency", LatencyEvaluator)
        self.register_evaluator("cost", CostEvaluator)
        self.register_evaluator("llm_judge", LLMJudgeEvaluator)
    
    def register_evaluator(self, name: str, evaluator_class: Type[BaseEvaluator]):
        """Register an evaluator class"""
        self._evaluators[name] = evaluator_class
        logger.info(f"Registered evaluator: {name}")
    
    def register_custom_evaluator(self, name: str, evaluator_func: Callable):
        """Register a custom evaluator function"""
        self._custom_evaluators[name] = evaluator_func
        logger.info(f"Registered custom evaluator: {name}")
    
    def get_available_evaluators(self) -> List[str]:
        """Get list of available evaluator names"""
        return list(self._evaluators.keys()) + list(self._custom_evaluators.keys())
    
    def create_evaluator(self, evaluator_type: str, config: Dict[str, Any]) -> BaseEvaluator:
        """Create an evaluator instance"""
        if evaluator_type in self._evaluators:
            evaluator_class = self._evaluators[evaluator_type]
            evaluator = evaluator_class(config)
            
            # Validate configuration
            if not evaluator.validate_config():
                raise ValueError(f"Invalid configuration for evaluator: {evaluator_type}")
            
            return evaluator
        elif evaluator_type in self._custom_evaluators:
            # For custom evaluators, return a wrapper
            return CustomEvaluatorWrapper(evaluator_type, self._custom_evaluators[evaluator_type], config)
        else:
            raise ValueError(f"Unknown evaluator type: {evaluator_type}")
    
    async def evaluate_single(self, evaluator_type: str, config: Dict[str, Any],
                            expected_output: str, actual_output: str,
                            input_data: Optional[Dict[str, Any]] = None,
                            execution_time_ms: Optional[float] = None,
                            cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Evaluate a single case with the specified evaluator"""
        try:
            evaluator = self.create_evaluator(evaluator_type, config)
            result = await evaluator.evaluate(
                expected_output=expected_output,
                actual_output=actual_output,
                input_data=input_data,
                execution_time_ms=execution_time_ms,
                cost_usd=cost_usd
            )
            return result
        except Exception as e:
            logger.error(f"Evaluation failed for {evaluator_type}: {e}")
            return {
                "evaluator_type": evaluator_type,
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }
    
    async def evaluate_batch(self, evaluator_configs: List[Dict[str, Any]],
                           test_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Evaluate multiple test cases with multiple evaluators"""
        results = []
        
        for test_case in test_cases:
            test_result = {
                "test_case": test_case,
                "evaluator_results": []
            }
            
            for evaluator_config in evaluator_configs:
                evaluator_type = evaluator_config.get("evaluator_type")
                config = evaluator_config.get("config", {})
                
                if not evaluator_type:
                    logger.error("Missing evaluator_type in config")
                    continue
                
                result = await self.evaluate_single(
                    evaluator_type=evaluator_type,
                    config=config,
                    expected_output=test_case.get("expected_output", ""),
                    actual_output=test_case.get("actual_output", ""),
                    input_data=test_case.get("input"),
                    execution_time_ms=test_case.get("latency_ms"),
                    cost_usd=test_case.get("cost_usd")
                )
                
                test_result["evaluator_results"].append(result)
            
            results.append(test_result)
        
        return results


class CustomEvaluatorWrapper(BaseEvaluator):
    """Wrapper for custom evaluator functions"""
    
    def __init__(self, name: str, evaluator_func: Callable, config: Dict[str, Any]):
        super().__init__(config)
        self.name = name
        self.evaluator_func = evaluator_func
    
    async def evaluate(self, expected_output: str, actual_output: str,
                      input_data: Optional[Dict[str, Any]] = None,
                      execution_time_ms: Optional[float] = None,
                      cost_usd: Optional[float] = None) -> Dict[str, Any]:
        """Call the custom evaluator function"""
        try:
            if asyncio.iscoroutinefunction(self.evaluator_func):
                result = await self.evaluator_func(
                    expected_output=expected_output,
                    actual_output=actual_output,
                    input_data=input_data,
                    execution_time_ms=execution_time_ms,
                    cost_usd=cost_usd,
                    config=self.config
                )
            else:
                result = self.evaluator_func(
                    expected_output=expected_output,
                    actual_output=actual_output,
                    input_data=input_data,
                    execution_time_ms=execution_time_ms,
                    cost_usd=cost_usd,
                    config=self.config
                )
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"score": float(result) if isinstance(result, (int, float)) else 0.0}
            
            result.setdefault("evaluator_type", self.name)
            result.setdefault("passed", result.get("score", 0.0) >= 0.5)
            
            return result
        except Exception as e:
            logger.error(f"Custom evaluator {self.name} error: {e}")
            return {
                "evaluator_type": self.name,
                "score": 0.0,
                "passed": False,
                "error": str(e)
            }


# Global evaluator service instance
evaluator_service = EvaluatorService() 