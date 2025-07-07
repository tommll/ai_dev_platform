# LLM Development Platform

A FastAPI-based platform for managing LLM experiments, evaluations, and production monitoring with Redis queuing and TimescaleDB for time-series metrics.

* Design doc: https://sugar-april-5dc.notion.site/LLM-development-platform-228723c39f3c802aa92fed196d4489dc?source=copy_link

## Features

- **Multi-tenant Architecture**: Organizations, projects, and user management
- **Prompt Management**: Version-controlled prompt templates
- **Dataset Management**: Structured evaluation datasets
- **Experiment Framework**: Configurable experiments with multiple evaluators
- **Background Processing**: Redis-based job queue for evaluation processing
- **Real-time Metrics**: TimescaleDB for time-series analytics
- **Production Monitoring**: Trace collection and observability

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Redis Queue   │    │   Evaluation    │
│   Application   │───▶│   (Jobs)        │───▶│   Workers       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │   TimescaleDB   │    │   AI Models     │
│   (Core Data)   │    │   (Metrics)     │    │   (OpenAI, etc) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd llm_dev_platform

# Create environment file
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, API)
docker-compose up -d

# Or start services individually
docker-compose up postgres redis -d
```

### 3. Run the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Start the FastAPI application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start the evaluation worker (in another terminal)
python worker.py
```

## API Usage

### 1. Submit an Evaluation Job

```python
import httpx
import json

# Job configuration
job_data = {
    "experiment_run_id": "run_123",
    "dataset_items": [
        {
            "input": {"question": "What is 2+2?"},
            "expected": "4",
            "metadata": {"category": "math"}
        },
        {
            "input": {"question": "What is the capital of France?"},
            "expected": "Paris",
            "metadata": {"category": "geography"}
        }
    ],
    "prompt_config": {
        "template": "Answer this question: {question}",
        "model": "gpt-3.5-turbo",
        "provider": "openai",
        "temperature": 0.7,
        "max_tokens": 100
    },
    "evaluators": [
        {
            "name": "exact_match",
            "config": {"case_sensitive": False}
        },
        {
            "name": "semantic_similarity",
            "config": {"threshold": 0.8}
        },
        {
            "name": "latency",
            "config": {"max_latency_ms": 5000}
        }
    ],
    "execution_config": {
        "timeout_seconds": 30,
        "max_retries": 3,
        "parallel_workers": 5
    }
}

# Submit job
async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://localhost:8000/api/v1/evaluation/jobs",
        json=job_data
    )
    job_response = response.json()
    print(f"Job submitted: {job_response['job_id']}")
```

### 2. Check Job Status

```python
# Check job status
job_id = job_response['job_id']
response = await client.get(f"http://localhost:8000/api/v1/evaluation/jobs/{job_id}/status")
status = response.json()
print(f"Job status: {status['status']}")
```

### 3. Monitor Progress

```python
# Check experiment run progress
run_id = "run_123"
response = await client.get(f"http://localhost:8000/api/v1/evaluation/runs/{run_id}/progress")
progress = response.json()
print(f"Progress: {progress['completed']}/{progress['total']} ({progress['percentage']:.1f}%)")
```

### 4. Get Results

```python
# Get evaluation results
response = await client.get(f"http://localhost:8000/api/v1/evaluation/runs/{run_id}/results")
results = response.json()
for result in results:
    print(f"Input: {result['input_data']}")
    print(f"Expected: {result['expected_output']}")
    print(f"Actual: {result['actual_output']}")
    print(f"Scores: {result['custom_metrics']}")
    print("---")
```

## Built-in Evaluators

### 1. Exact Match
```python
{
    "name": "exact_match",
    "config": {
        "case_sensitive": False
    }
}
```

### 2. Semantic Similarity
```python
{
    "name": "semantic_similarity",
    "config": {
        "threshold": 0.8
    }
}
```

### 3. LLM Judge
```python
{
    "name": "llm_judge",
    "config": {
        "judge_model": "gpt-3.5-turbo",
        "threshold": 0.7,
        "api_key": "your-openai-key"
    }
}
```

### 4. Latency Evaluator
```python
{
    "name": "latency",
    "config": {
        "max_latency_ms": 5000
    }
}
```

### 5. Cost Evaluator
```python
{
    "name": "cost",
    "config": {
        "max_cost_usd": 0.10
    }
}
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5433/llm_platform

# Redis
REDIS_URL=redis://localhost:6378

# API Keys
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Authentication
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=["http://localhost:3000"]
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy app/
```

## Production Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling Workers

```bash
# Run multiple worker instances
python worker.py  # Worker 1
python worker.py  # Worker 2
python worker.py  # Worker 3
```

## API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

The platform uses PostgreSQL with TimescaleDB extension for time-series data:

- **Core Tables**: organizations, users, projects, prompts, datasets, experiments
- **Time-series Tables**: eval_metrics, trace_metrics, usage_metrics
- **Evaluation Tables**: evaluation_results, experiment_runs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License 
