import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.experiment import ExperimentRun, RunStatus
from app.models.evaluation import EvaluationResult
from app.models.dataset import DatasetItem
from app.services.redis_queue import RedisQueue
from app.services.evaluator_framework import EvaluatorFramework
from app.services.ai_model_service import AIModelService


class EvaluationWorker:
    """Main evaluation worker that processes jobs from Redis queue"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis_queue = RedisQueue()
        self.evaluator_framework = EvaluatorFramework()
        self.ai_model_service = AIModelService()
        self.running = False
    
    async def start(self):
        """Start the worker loop"""
        self.running = True
        print("Evaluation worker started")
        
        while self.running:
            try:
                # Dequeue job
                job_data = await self.redis_queue.dequeue_job()
                if job_data:
                    await self.process_evaluation_job(job_data)
                else:
                    # No jobs, wait a bit
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"Worker error: {e}")
                await asyncio.sleep(5)
    
    async def stop(self):
        """Stop the worker"""
        self.running = False
        await self.redis_queue.close()
    
    async def process_evaluation_job(self, job_data: Dict[str, Any]):
        """Process a single evaluation job"""
        job_id = job_data.get("job_id")
        experiment_run_id = job_data.get("experiment_run_id")
        
        try:
            # Update job status
            await self.redis_queue.update_job_status(job_id, "running")
            
            # Get experiment run
            run = await self._get_experiment_run(experiment_run_id)
            if not run:
                raise ValueError(f"Experiment run not found: {experiment_run_id}")
            
            # Update run status
            await self._update_run_status(run.id, RunStatus.RUNNING)
            
            # Process dataset items
            dataset_items = job_data.get("dataset_items", [])
            total_items = len(dataset_items)
            
            if total_items == 0:
                raise ValueError("No dataset items provided")
            
            results = []
            completed = 0
            
            # Process in batches
            batch_size = job_data.get("execution_config", {}).get("parallel_workers", 5)
            
            for batch in self._batch_items(dataset_items, batch_size):
                batch_results = await self._process_batch(batch, job_data)
                results.extend(batch_results)
                
                completed += len(batch)
                await self._update_progress(experiment_run_id, completed, total_items)
            
            # Aggregate results
            aggregated_metrics = self._aggregate_results(results)
            
            # Update experiment run with final results
            await self._update_run_completion(run.id, aggregated_metrics, total_items, len(results))
            
            # Update job status
            await self.redis_queue.update_job_status(job_id, "completed")
            
            print(f"Job {job_id} completed successfully")
            
        except Exception as e:
            print(f"Job {job_id} failed: {e}")
            await self.redis_queue.update_job_status(job_id, "failed")
            
            # Update run status if we have the run
            if experiment_run_id:
                run = await self._get_experiment_run(experiment_run_id)
                if run:
                    await self._update_run_status(run.id, RunStatus.FAILED)
    
    def _batch_items(self, items: List[Dict[str, Any]], batch_size: int):
        """Split items into batches"""
        for i in range(0, len(items), batch_size):
            yield items[i:i + batch_size]
    
    async def _process_batch(self, items: List[Dict[str, Any]], job_data: Dict[str, Any]) -> List[EvaluationResult]:
        """Process a batch of items concurrently"""
        tasks = []
        for item in items:
            task = self._evaluate_single_item(item, job_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and return valid results
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                print(f"Item evaluation failed: {result}")
            else:
                valid_results.append(result)
        
        return valid_results
    
    async def _evaluate_single_item(self, item: Dict[str, Any], job_data: Dict[str, Any]) -> EvaluationResult:
        """Evaluate a single dataset item"""
        experiment_run_id = job_data.get("experiment_run_id")
        prompt_config = job_data.get("prompt_config", {})
        evaluators = job_data.get("evaluators", [])
        
        input_data = item.get("input", {})
        expected_output = item.get("expected", "")
        
        # Call AI model
        model_result = await self.ai_model_service.call_model(prompt_config, input_data)
        
        if model_result.get("error"):
            # Handle model error
            return await self._create_error_result(
                experiment_run_id, input_data, expected_output, model_result["error"]
            )
        
        actual_output = model_result["output"]
        execution_time_ms = model_result["execution_time_ms"]
        cost_usd = model_result["cost_usd"]
        
        # Run evaluators
        scores = {}
        for evaluator_config in evaluators:
            evaluator_result = await self.evaluator_framework.run_evaluator(
                evaluator_config,
                input_data,
                expected_output,
                actual_output,
                execution_time_ms,
                cost_usd
            )
            scores[evaluator_config["name"]] = evaluator_result
        
        # Create evaluation result
        result = EvaluationResult(
            experiment_run_id=experiment_run_id,
            input_data=input_data,
            expected_output=expected_output,
            actual_output=actual_output,
            custom_metrics=scores,
            latency_ms=execution_time_ms,
            cost_usd=cost_usd,
            is_success=True,
            created_at=datetime.utcnow()
        )
        
        # Save to database
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        return result
    
    async def _create_error_result(self, experiment_run_id: str, input_data: Dict[str, Any], 
                                 expected_output: str, error_message: str) -> EvaluationResult:
        """Create an error result when evaluation fails"""
        result = EvaluationResult(
            experiment_run_id=experiment_run_id,
            input_data=input_data,
            expected_output=expected_output,
            actual_output=None,
            custom_metrics={},
            latency_ms=0.0,
            cost_usd=0.0,
            is_success=False,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        
        self.db.add(result)
        await self.db.commit()
        await self.db.refresh(result)
        
        return result
    
    def _aggregate_results(self, results: List[EvaluationResult]) -> Dict[str, Any]:
        """Aggregate evaluation results into summary metrics"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r.is_success]
        failed_results = [r for r in results if not r.is_success]
        
        # Basic metrics
        total_count = len(results)
        success_count = len(successful_results)
        failure_count = len(failed_results)
        
        aggregated = {
            "total_items": total_count,
            "successful_items": success_count,
            "failed_items": failure_count,
            "success_rate": success_count / total_count if total_count > 0 else 0.0,
            "avg_latency_ms": 0.0,
            "total_cost_usd": 0.0,
            "evaluator_scores": {}
        }
        
        if successful_results:
            # Calculate averages
            total_latency = sum(r.latency_ms for r in successful_results)
            total_cost = sum(r.cost_usd for r in successful_results)
            
            aggregated["avg_latency_ms"] = total_latency / len(successful_results)
            aggregated["total_cost_usd"] = total_cost
            
            # Aggregate evaluator scores
            evaluator_scores = {}
            for result in successful_results:
                if result.custom_metrics:
                    for evaluator_name, evaluator_result in result.custom_metrics.items():
                        if evaluator_name not in evaluator_scores:
                            evaluator_scores[evaluator_name] = []
                        if isinstance(evaluator_result, dict) and "score" in evaluator_result:
                            evaluator_scores[evaluator_name].append(evaluator_result["score"])
            
            # Calculate average scores for each evaluator
            for evaluator_name, scores in evaluator_scores.items():
                if scores:
                    aggregated["evaluator_scores"][evaluator_name] = {
                        "avg_score": sum(scores) / len(scores),
                        "min_score": min(scores),
                        "max_score": max(scores)
                    }
        
        return aggregated
    
    async def _get_experiment_run(self, run_id: str) -> Optional[ExperimentRun]:
        """Get experiment run by ID"""
        stmt = select(ExperimentRun).where(ExperimentRun.run_id == run_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _update_run_status(self, run_id: int, status: RunStatus):
        """Update experiment run status"""
        stmt = update(ExperimentRun).where(ExperimentRun.id == run_id).values(
            status=status,
            started_at=datetime.utcnow() if status == RunStatus.RUNNING else None
        )
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def _update_run_completion(self, run_id: int, metrics: Dict[str, Any], 
                                   total_items: int, completed_items: int):
        """Update experiment run with completion data"""
        stmt = update(ExperimentRun).where(ExperimentRun.id == run_id).values(
            status=RunStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            total_items=total_items,
            completed_items=completed_items,
            metrics=metrics
        )
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def _update_progress(self, run_id: str, completed: int, total: int):
        """Update progress in Redis"""
        await self.redis_queue.store_progress(run_id, completed, total) 