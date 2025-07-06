#!/usr/bin/env python3
"""
Test script for evaluation worker
Run this to test your worker functionality
"""
import random
import asyncio
import sys
import json
import time
import uuid
from typing import Dict, Any, List
import redis
import redis.asyncio as redis_async
from app.config import settings
from app.services.redis_queue import RedisQueue
from app.services.evaluation_worker import EvaluationWorker
from app.services.evaluator_service import evaluator_service
from app.database import AsyncSessionLocal, test_async_connection
from app.models.experiment import ExperimentRun, RunStatus, Experiment, ExperimentStatus
import pdb

class WorkerTester:
    def __init__(self):
        self.redis_url = settings.redis_url
        self.queue_service = RedisQueue()
        self.db = AsyncSessionLocal()
        self.worker = EvaluationWorker(self.db)
        self.test_results = {}
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
        if message:
            print(f"   {message}")
        self.test_results[test_name] = success
        return success

    async def test_simple_evaluation_job(self) -> bool:
        """Test simple evaluation job processing"""
        print("\n🔍 Testing simple evaluation job...")
        
        test_run = None
        test_experiment = None
        try:
            # Create a test experiment run record in the database
            async with self.db as session:
                # First create a test experiment
                test_experiment = Experiment(
                    name="Test Evaluation Experiment",
                    description="Test experiment for worker testing",
                    status=ExperimentStatus.ACTIVE,
                    prompt_id=1,  # Assuming prompt ID 1 exists
                    dataset_id=1,  # Assuming dataset ID 1 exists
                    model_configuration={
                        "provider": "openai",
                        "model": "gpt-3.5-turbo",
                        "temperature": 0.7
                    },
                    evaluation_config={
                        "metrics": ["accuracy", "relevance"],
                        "thresholds": {"accuracy": 0.8}
                    },
                    project_id=1  # Assuming project ID 1 exists
                )
                
                session.add(test_experiment)
                await session.commit()
                await session.refresh(test_experiment)
                
                print(f"✅ Created test experiment: {test_experiment.name} (ID: {test_experiment.id})")
                
                # Create a test experiment run
                test_run = ExperimentRun(
                    id=str(uuid.uuid4()),
                    status=RunStatus.PENDING,
                    total_items=2,
                    completed_items=0,
                    failed_items=0,
                    experiment_id=test_experiment.id
                )
                
                session.add(test_run)
                await session.commit()
                await session.refresh(test_run)
                
                print(f"✅ Created experiment run: {test_run.id} (ID: {test_run.id})")
                
                # Use the created run ID for the test job
                job_id = str(uuid.uuid4())
                test_job = {
                    "job_id": job_id,
                    "experiment_run_id": test_run.id,
                    "evaluator_configs": [
                        {
                            "evaluator_type": "exact_match",
                            "config": {
                                "case_sensitive": False,
                                "strip_whitespace": True
                            }
                        }
                    ],
                    "test_cases": [
                        {
                            "input": "What is the capital of France?",
                            "expected_output": "Paris",
                            "actual_output": "Paris"
                        },
                        {
                            "input": "What is 2+2?",
                            "expected_output": "4",
                            "actual_output": "4"
                        }
                    ],
                    "dataset_ids": [
                        1,
                    ]

                }
                test_job["evaluator_configs"] = json.dumps(test_job["evaluator_configs"])
                test_job['test_cases'] = json.dumps(test_job['test_cases'])
                test_job['dataset_ids'] = json.dumps(test_job['dataset_ids'])
            
            # Enqueue job
            await self.queue_service.enqueue_job(test_job)

            print(f"✅ Job enqueued: {job_id}")
            
            # Process job
            result = await self.worker.process_evaluation_job(test_job)
            
            if result and result.get("status") == "completed":
                results = result.get("results", [])
                print(f"✅ Job processed successfully: {len(results)} results")
                print(f"✅ Job result: {result}")
                return self.log_test("Simple Evaluation Job", True, f"Processed {len(results)} test cases")
            else:
                return self.log_test("Simple Evaluation Job", False, f"Processing failed: {result}")
                
        except Exception as e:
            return self.log_test("Simple Evaluation Job", False, f"Error: {e}")
        finally:
            # Clean up: Delete the test run and experiment records
            if test_run or test_experiment:
                try:
                    async with self.db as session:
                        if test_run:
                            # Delete the test run
                            await session.delete(test_run)
                            print(f"✅ Cleaned up test run: {test_run.id}")
                        
                        if test_experiment:
                            # Delete the test experiment
                            await session.delete(test_experiment)
                            print(f"✅ Cleaned up test experiment: {test_experiment.name}")
                        
                        await session.commit()
                except Exception as cleanup_error:
                    print(f"⚠️  Failed to cleanup test data: {cleanup_error}")

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all worker tests"""
        print("🚀 Starting Worker Tests")
        print("=" * 60)
        print("Testing evaluation worker functionality")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_simple_evaluation_job,
        ]
        
        for test in tests:
            await test()
        
        return self.test_results

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📋 Worker Test Summary:")
        print("=" * 60)
        
        passed = sum(1 for success in self.test_results.values() if success)
        total = len(self.test_results)
        
        for test_name, success in self.test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{test_name:<30} {status}")
        
        print("-" * 60)
        print(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 All tests passed! Worker is working correctly.")
            return True
        else:
            print(f"\n⚠️  {total - passed} test(s) failed. Please check your worker configuration.")
            return False


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test evaluation worker")
    parser.add_argument("--redis-url", default=None,
                       help="Redis URL (default: from settings)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    
    args = parser.parse_args()
    
    # Override Redis URL if provided
    if args.redis_url:
        settings.redis_url = args.redis_url
    
    # Create tester
    tester = WorkerTester()
    
    # Run tests
    results = await tester.run_all_tests()
    
    # Print summary
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main()) 