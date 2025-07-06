#!/usr/bin/env python3
"""
Standalone evaluation worker script.
Run this to start the evaluation worker independently of the FastAPI app.
"""

import asyncio
import signal
import sys
from app.database import AsyncSessionLocal
from app.services.evaluation_worker import EvaluationWorker


async def main():
    """Main worker function"""
    print("Starting evaluation worker...")
    
    # Create database session
    async with AsyncSessionLocal() as db:
        worker = EvaluationWorker(db)
        
        # Handle shutdown gracefully
        def signal_handler(signum, frame):
            print("\nReceived shutdown signal, stopping worker...")
            asyncio.create_task(worker.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            await worker.start()
        except KeyboardInterrupt:
            print("\nWorker interrupted by user")
        except Exception as e:
            print(f"Worker error: {e}")
        finally:
            await worker.stop()
            print("Worker stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nWorker stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1) 