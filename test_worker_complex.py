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

    async def test_redis_connection(self) -> bool:
        """Test Redis connection for worker"""
        print("\n🔍 Testing Redis connection for worker...")
        
        try:
            r = redis_async.from_url(self.redis_url)
            await r.ping()
            await r.close()
            return self.log_test("Redis Connection", True, "Connected successfully")
        except Exception as e:
            return self.log_test("Redis Connection", False, f"Error: {e}")

    async def test_database_connection(self) -> bool:
        """Test PostgreSQL database connection for worker"""
        print("\n🔍 Testing PostgreSQL database connection for worker...")
        
        try:
            # Test async database connection
            success = await test_async_connection()
            if success:
                return self.log_test("Database Connection", True, "Connected successfully")
            else:
                return self.log_test("Database Connection", False, "Connection failed")
        except Exception as e:
            return self.log_test("Database Connection", False, f"Error: {e}")

    async def test_database_operations(self) -> bool:
        """Test basic database operations"""
        print("\n🔍 Testing database operations...")
        
        try:
            from sqlalchemy import text
            
            # Test database session
            async with self.db as session:
                # Test simple query

                result = await session.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                if row and row[0] == 1:
                    print("✅ Database session and query working")
                    return self.log_test("Database Operations", True, "Session and query successful")
                else:
                    return self.log_test("Database Operations", False, "Query result unexpected")
                    
        except Exception as e:
            return self.log_test("Database Operations", False, f"Error: {e}")

    async def test_queue_service(self) -> bool:
        """Test queue service functionality"""
        print("\n🔍 Testing queue service...")
        
        try:
            # Test enqueue
            test_job = {
                "job_id": str(uuid.uuid4()),
                "data": {"test": "data"}
            }
            
            await self.queue_service.enqueue_job(test_job)
            print("✅ Job enqueued successfully")
            
            # Test dequeue
            job = await self.queue_service.dequeue_job("test_queue")
            if job and job.get("data", {}).get("test") == "data":
                print("✅ Job dequeued successfully")
                return self.log_test("Queue Service", True, "Enqueue/Dequeue working")
            else:
                return self.log_test("Queue Service", False, "Dequeue failed")
                
        except Exception as e:
            return self.log_test("Queue Service", False, f"Error: {e}")

    async def test_evaluator_service(self) -> bool:
        """Test evaluator service functionality"""
        print("\n🔍 Testing evaluator service...")
        
        try:
            # Test exact match evaluator
            exact_config = {"case_sensitive": False, "strip_whitespace": True}
            result = await evaluator_service.evaluate_single(
                "exact_match", exact_config, "hello", "HELLO"
            )
            print(f"✅ Exact match evaluator: {result}")
            
            # Test semantic similarity evaluator
            semantic_config = {"threshold": 0.8}
            result = await evaluator_service.evaluate_single(
                "semantic_similarity", semantic_config, "hello world", "hi world"
            )
            print(f"✅ Semantic similarity evaluator: {result}")
            
            # Test latency evaluator
            latency_config = {"max_latency_ms": 1000}
            result = await evaluator_service.evaluate_single(
                "latency", latency_config, "test", "test", execution_time_ms=500
            )
            print(f"✅ Latency evaluator: {result}")
            
            return self.log_test("Evaluator Service", True, "All evaluators created successfully")
            
        except Exception as e:
            return self.log_test("Evaluator Service", False, f"Error: {e}")

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
            
            # pdb.set_trace()
            if result and result.get("status") == "completed":
                results = result.get("results", [])
                print(f"✅ Job processed successfully: {len(results)} results")
                print(f"✅ Job result: {result}")
                return self.log_test("Simple Evaluation Job", True, f"Processed {len(results)} test cases")
            else:
                return self.log_test("Simple Evaluation Job", False, f"Processing failed: {result}")
                
        except Exception as e:
            # pdb.set_trace()
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

    async def test_complex_evaluation_job(self) -> bool:
        """Test complex evaluation job with multiple evaluators"""
        print("\n🔍 Testing complex evaluation job...")
        
        try:
            job_id = str(uuid.uuid4())
            test_job = {
                "job_id": job_id,
                "experiment_run_id": "test-run-complex",
                "evaluator_configs": [
                    {
                        "evaluator_type": "exact_match",
                        "config": {
                            "case_sensitive": False,
                            "strip_whitespace": True
                        }
                    },
                    {
                        "evaluator_type": "latency",
                        "config": {
                            "max_latency_ms": 1000
                        }
                    },
                    {
                        "evaluator_type": "cost",
                        "config": {
                            "max_cost_usd": 0.01
                        }
                    }
                ],
                "test_cases": [
                    {
                        "input": "Hello world",
                        "expected_output": "Hello world",
                        "actual_output": "hello world",
                        "latency_ms": 500,
                        "cost_usd": 0.005
                    },
                    {
                        "input": "Test case 2",
                        "expected_output": "Expected result",
                        "actual_output": "Different result",
                        "latency_ms": 800,
                        "cost_usd": 0.008
                    }
                ]
            }
            
            # Process job
            result = await self.worker.process_job(test_job)
            
            if result and result.get("status") == "completed":
                results = result.get("results", [])
                print(f"✅ Complex job processed: {len(results)} results")
                
                # Check if all evaluators ran
                evaluator_types = set()
                for test_result in results:
                    for eval_result in test_result.get("evaluator_results", []):
                        evaluator_types.add(eval_result.get("evaluator_type"))
                
                print(f"✅ Evaluators used: {evaluator_types}")
                return self.log_test("Complex Evaluation Job", True, f"Processed with {len(evaluator_types)} evaluators")
            else:
                return self.log_test("Complex Evaluation Job", False, f"Processing failed: {result}")
                
        except Exception as e:
            return self.log_test("Complex Evaluation Job", False, f"Error: {e}")

    async def test_worker_error_handling(self) -> bool:
        """Test worker error handling"""
        print("\n🔍 Testing worker error handling...")
        
        try:
            # Test with invalid job data
            invalid_job = {
                "job_id": str(uuid.uuid4()),
                "experiment_run_id": "test-error",
                "evaluator_configs": [
                    {
                        "evaluator_type": "nonexistent_evaluator",
                        "config": {}
                    }
                ],
                "test_cases": []
            }
            
            result = await self.worker.process_job(invalid_job)
            
            if result and result.get("status") == "failed":
                print("✅ Error handling works for invalid evaluator")
                return self.log_test("Error Handling", True, "Invalid evaluator handled correctly")
            else:
                return self.log_test("Error Handling", False, "Expected error not caught")
                
        except Exception as e:
            return self.log_test("Error Handling", False, f"Error: {e}")

    async def test_worker_performance(self) -> bool:
        """Test worker performance with multiple jobs"""
        print("\n🔍 Testing worker performance...")
        
        try:
            start_time = time.time()
            
            # Create multiple simple jobs
            jobs = []
            for i in range(5):
                job = {
                    "job_id": str(uuid.uuid4()),
                    "experiment_run_id": f"perf-test-{i}",
                    "evaluator_configs": [
                        {
                            "evaluator_type": "exact_match",
                            "config": {"case_sensitive": False}
                        }
                    ],
                    "test_cases": [
                        {
                            "input": f"Test {i}",
                            "expected_output": f"Result {i}",
                            "actual_output": f"Result {i}"
                        }
                    ]
                }
                jobs.append(job)
            
            # Process all jobs
            results = []
            for job in jobs:
                result = await self.worker.process_job(job)
                results.append(result)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            successful_jobs = sum(1 for r in results if r and r.get("status") == "completed")
            print(f"✅ Processed {successful_jobs}/{len(jobs)} jobs in {total_time:.2f}s")
            
            return self.log_test("Worker Performance", True, f"Processed {successful_jobs} jobs in {total_time:.2f}s")
            
        except Exception as e:
            return self.log_test("Worker Performance", False, f"Error: {e}")

    async def test_worker_concurrent_processing(self) -> bool:
        """Test concurrent job processing"""
        print("\n🔍 Testing concurrent job processing...")
        
        try:
            # Create multiple jobs
            jobs = []
            for i in range(3):
                job = {
                    "job_id": str(uuid.uuid4()),
                    "experiment_run_id": f"concurrent-test-{i}",
                    "evaluator_configs": [
                        {
                            "evaluator_type": "exact_match",
                            "config": {"case_sensitive": False}
                        }
                    ],
                    "test_cases": [
                        {
                            "input": f"Concurrent test {i}",
                            "expected_output": f"Result {i}",
                            "actual_output": f"Result {i}"
                        }
                    ]
                }
                jobs.append(job)
            
            # Process jobs concurrently
            start_time = time.time()
            tasks = [self.worker.process_job(job) for job in jobs]
            results = await asyncio.gather(*tasks)
            end_time = time.time()
            
            concurrent_time = end_time - start_time
            successful_jobs = sum(1 for r in results if r and r.get("status") == "completed")
            
            print(f"✅ Concurrent processing: {successful_jobs}/{len(jobs)} jobs in {concurrent_time:.2f}s")
            
            return self.log_test("Concurrent Processing", True, f"Processed {successful_jobs} jobs concurrently")
            
        except Exception as e:
            return self.log_test("Concurrent Processing", False, f"Error: {e}")

    async def test_worker_memory_usage(self) -> bool:
        """Test worker memory usage"""
        print("\n🔍 Testing worker memory usage...")
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Process a large job
            large_job = {
                "job_id": str(uuid.uuid4()),
                "experiment_run_id": "memory-test",
                "evaluator_configs": [
                    {
                        "evaluator_type": "exact_match",
                        "config": {"case_sensitive": False}
                    }
                ],
                "test_cases": [
                    {
                        "input": "x" * 1000,  # Large input
                        "expected_output": "y" * 1000,  # Large output
                        "actual_output": "y" * 1000
                    } for _ in range(100)  # Many test cases
                ]
            }
            
            result = await self.worker.process_job(large_job)
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            print(f"✅ Memory usage: {initial_memory:.1f}MB -> {final_memory:.1f}MB (+{memory_increase:.1f}MB)")
            
            if memory_increase < 50:  # Less than 50MB increase
                return self.log_test("Memory Usage", True, f"Memory increase: {memory_increase:.1f}MB")
            else:
                return self.log_test("Memory Usage", False, f"High memory usage: {memory_increase:.1f}MB")
                
        except ImportError:
            return self.log_test("Memory Usage", False, "psutil not installed")
        except Exception as e:
            return self.log_test("Memory Usage", False, f"Error: {e}")

    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all worker tests"""
        print("🚀 Starting Worker Tests")
        print("=" * 60)
        print("Testing evaluation worker functionality")
        print("=" * 60)
        
        # Run all tests
        tests = [
            # self.test_redis_connection,
            # self.test_database_connection,
            # self.test_database_operations, # Added this line
            # self.test_queue_service,
            # self.test_evaluator_service,
            self.test_simple_evaluation_job,
            # self.test_complex_evaluation_job,
            # self.test_worker_error_handling,
            # self.test_worker_performance,
            # self.test_worker_concurrent_processing,
        ]
        
        # Add memory test if psutil is available
        # try:
        #     import psutil
        #     tests.append(self.test_worker_memory_usage)
        # except ImportError:
        #     print("⚠️  psutil not installed, skipping memory usage test")
        
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