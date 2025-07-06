import json
import uuid
from typing import Optional, Dict, Any
import redis.asyncio as redis
from app.config import settings


class RedisQueue:
    def __init__(self):
        self.redis_client = redis.from_url(settings.redis_url)
        self.evaluation_queue = "evaluation_jobs"
        self.progress_prefix = "progress:"
        self.job_prefix = "job:"
    
    async def enqueue_job(self, job_data: Dict[str, Any]) -> str:
        """Enqueue an evaluation job and return job ID"""
        job_id = str(uuid.uuid4())
        job_data["job_id"] = job_id
        job_data["status"] = "queued"
        job_data["created_at"] = str(uuid.uuid1().time)
        
        # Store job details
        await self.redis_client.hset(
            f"{self.job_prefix}{job_id}",
            mapping=job_data
        )
        
        # Add to queue
        await self.redis_client.lpush(self.evaluation_queue, job_id)
        
        return job_id
    
    async def dequeue_job(self) -> Optional[Dict[str, Any]]:
        """Dequeue next job from the queue"""
        job_id = await self.redis_client.rpop(self.evaluation_queue)
        if not job_id:
            return None
        
        job_data = await self.redis_client.hgetall(f"{self.job_prefix}{job_id.decode()}")
        if job_data:
            # Convert bytes to strings
            return {k.decode(): v.decode() if isinstance(v, bytes) else v 
                   for k, v in job_data.items()}
        return None
    
    async def update_job_status(self, job_id: str, status: str, progress: Optional[int] = None):
        """Update job status and progress"""
        await self.redis_client.hset(f"{self.job_prefix}{job_id}", "status", status)
        if progress is not None:
            await self.redis_client.hset(f"{self.job_prefix}{job_id}", "progress", progress)
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status and progress"""
        job_data = await self.redis_client.hgetall(f"{self.job_prefix}{job_id}")
        if job_data:
            return {k.decode(): v.decode() if isinstance(v, bytes) else v 
                   for k, v in job_data.items()}
        return None
    
    async def store_progress(self, run_id: str, completed: int, total: int):
        """Store experiment run progress"""
        progress_data = {
            "completed": completed,
            "total": total,
            "percentage": (completed / total * 100) if total > 0 else 0
        }
        await self.redis_client.hset(
            f"{self.progress_prefix}{run_id}",
            mapping=progress_data
        )
    
    async def get_progress(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get experiment run progress"""
        progress_data = await self.redis_client.hgetall(f"{self.progress_prefix}{run_id}")
        if progress_data:
            return {k.decode(): int(v.decode()) if k.decode() in ["completed", "total"] else float(v.decode())
                   for k, v in progress_data.items()}
        return None
    
    async def close(self):
        """Close Redis connection"""
        await self.redis_client.close() 