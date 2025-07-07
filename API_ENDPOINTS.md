# LLM Development Platform API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All endpoints except `/auth/login` require authentication via Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

---

## Authentication & Users

### POST /auth/login
Login user and get access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### GET /users/me
Get current user information.

**Response:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "username",
  "full_name": "Full Name",
  "is_active": true,
  "is_superuser": false,
  "organization_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

### PUT /users/me/preferences
Update current user preferences.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Full Name"
}
```

### GET /organizations/{organization_id}/members
Get members of an organization.

**Response:**
```json
{
  "organization": {
    "id": 1,
    "name": "Organization Name",
    "slug": "org-slug"
  },
  "members": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "username",
      "full_name": "Full Name",
      "is_active": true,
      "is_superuser": false,
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

---

## Prompt Management

### GET /projects/{project_id}/prompts
Get all prompts for a project.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Customer Support Prompt",
    "description": "Prompt for customer support queries",
    "is_active": true,
    "is_deployed": true,
    "project_id": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /projects/{project_id}/prompts
Create a new prompt for a project.

**Request Body:**
```json
{
  "name": "New Prompt",
  "description": "Description of the prompt",
  "project_id": 1
}
```

### GET /prompts/{prompt_id}/versions
Get all versions of a prompt.

**Response:**
```json
[
  {
    "id": 1,
    "version": "v1.0",
    "template": "You are a helpful assistant. Please help with: {{query}}",
    "variables": {
      "query": {"type": "string", "required": true}
    },
    "is_deployed": true,
    "prompt_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### POST /prompts/{prompt_id}/versions
Create a new version of a prompt.

**Request Body:**
```json
{
  "version": "v1.1",
  "template": "You are a helpful assistant. Please help with: {{query}}",
  "variables": {
    "query": {"type": "string", "required": true}
  },
  "prompt_id": 1
}
```

### PUT /prompts/{prompt_id}/versions/{version}/deploy
Deploy a specific version of a prompt.

**Response:**
```json
{
  "message": "Version v1.1 deployed successfully",
  "prompt_id": 1,
  "version": "v1.1"
}
```

---

## Dataset Management

### GET /projects/{project_id}/datasets
Get all datasets for a project.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Customer Queries Dataset",
    "description": "Dataset of customer support queries",
    "is_active": true,
    "project_id": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": null
  }
]
```

### POST /projects/{project_id}/datasets
Create a new dataset for a project.

**Request Body:**
```json
{
  "name": "New Dataset",
  "description": "Description of the dataset",
  "project_id": 1
}
```

### POST /datasets/{dataset_id}/upload
Upload a file to create dataset items.

**Request:** Multipart form data with file upload.

**Supported formats:** JSON, CSV

**JSON format:**
```json
[
  {
    "input_data": {"query": "How do I reset my password?"},
    "expected_output": "To reset your password, go to the login page..."
  }
]
```

**CSV format:** First column as input_data, second column as expected_output.

**Response:**
```json
{
  "message": "Successfully uploaded 100 items",
  "dataset_id": 1,
  "items_created": 100
}
```

### GET /datasets/{dataset_id}/items
Get dataset items with pagination.

**Query Parameters:**
- `limit` (int, default: 100, max: 1000)
- `offset` (int, default: 0)

**Response:**
```json
[
  {
    "id": 1,
    "input_data": {"query": "How do I reset my password?"},
    "expected_output": "To reset your password, go to the login page...",
    "dataset_id": 1,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

### POST /datasets/{dataset_id}/items/bulk
Create multiple dataset items in bulk.

**Request Body:**
```json
{
  "items": [
    {
      "input_data": {"query": "How do I reset my password?"},
      "expected_output": "To reset your password, go to the login page..."
    }
  ]
}
```

---

## Experiment Execution

### POST /experiments
Create a new experiment.

**Request Body:**
```json
{
  "name": "Customer Support Experiment",
  "description": "Testing customer support prompt performance",
  "prompt_id": 1,
  "dataset_id": 1,
  "model_configuration": {
    "provider": "openai",
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000
  },
  "evaluation_config": {
    "metrics": ["accuracy", "latency", "cost"],
    "thresholds": {
      "accuracy": 0.8,
      "latency": 2000
    }
  },
  "project_id": 1
}
```

### POST /experiments/{experiment_id}/runs
Create and start a new experiment run.

**Request Body:**
```json
{
  "experiment_id": 1
}
```

**Response:**
```json
{
  "id": "run_abc12345",
  "run_id": "run_abc12345",
  "status": "pending",
  "total_items": 0,
  "completed_items": 0,
  "failed_items": 0,
  "metrics": null,
  "experiment_id": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

### GET /experiments/{experiment_id}/runs/{run_id}/status
Get the status of an experiment run.

**Response:**
```json
{
  "run_id": "run_abc12345",
  "status": "running",
  "total_items": 100,
  "completed_items": 45,
  "failed_items": 2,
  "progress_percentage": 45.0,
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": "2024-01-01T00:01:00Z",
  "completed_at": null
}
```

### GET /experiments/{experiment_id}/runs/{run_id}/results
Get the results of an experiment run.

**Response:**
```json
{
  "run_id": "run_abc12345",
  "status": "completed",
  "metrics": {
    "accuracy": 0.85,
    "latency": 1500.5,
    "cost": 0.025
  },
  "total_items": 100,
  "completed_items": 100,
  "failed_items": 0,
  "evaluation_results": [
    {
      "id": 1,
      "dataset_item_id": 1,
      "input_data": {"query": "How do I reset my password?"},
      "output_data": {"response": "To reset your password..."},
      "metrics": {"accuracy": 0.9, "latency": 1200},
      "is_success": true,
      "error_message": null,
      "created_at": "2024-01-01T00:02:00Z"
    }
  ],
  "created_at": "2024-01-01T00:00:00Z",
  "started_at": "2024-01-01T00:01:00Z",
  "completed_at": "2024-01-01T00:05:00Z"
}
```

### POST /experiments/{experiment_id}/runs/{run_id}/cancel
Cancel an experiment run.

**Response:**
```json
{
  "message": "Experiment run cancelled successfully",
  "run_id": "run_abc12345",
  "status": "cancelled"
}
```

---

## Observability

### POST /traces
Submit a production trace.

**Request Body:**
```json
{
  "prompt_id": 1,
  "input_data": {"query": "How do I reset my password?"},
  "output_data": {"response": "To reset your password..."},
  "latency_ms": 1250.5,
  "tokens_used": 45,
  "cost_usd": 0.0025,
  "model_name": "gpt-3.5-turbo",
  "model_provider": "openai",
  "is_success": true,
  "error_message": null
}
```

**Response:**
```json
{
  "trace_id": "trace_abc12345",
  "message": "Trace submitted successfully"
}
```

### GET /projects/{project_id}/metrics
Query metrics for a project.

**Query Parameters:**
- `metric_type` (required): "eval", "trace", or "usage"
- `start_time` (optional): ISO datetime
- `end_time` (optional): ISO datetime
- `interval` (optional): Time interval for aggregation (default: "1 hour")

**Example:**
```
GET /projects/1/metrics?metric_type=trace&interval=1 hour
```

**Response:**
```json
{
  "metrics": [
    {
      "bucket": "2024-01-01T10:00:00Z",
      "model": "gpt-3.5-turbo",
      "avg_latency": 1250.5,
      "max_latency": 2000.0,
      "min_latency": 800.0,
      "total_cost": 0.025,
      "request_count": 100
    }
  ]
}
```

### POST /projects/{project_id}/alerts
Create an alert rule for a project.

**Request Body:**
```json
{
  "name": "High Latency Alert",
  "description": "Alert when average latency exceeds 2000ms",
  "metric_name": "latency_ms",
  "threshold": 2000.0,
  "operator": "gt",
  "time_window_minutes": 60,
  "is_active": true
}
```

### GET /projects/{project_id}/alerts
List active alerts for a project.

**Response:**
```json
{
  "alerts": [
    {
      "id": 1,
      "name": "High Latency Alert",
      "description": "Alert when average latency exceeds 2000ms",
      "metric_name": "latency_ms",
      "threshold": 2000.0,
      "operator": "gt",
      "time_window_minutes": 60,
      "is_active": true,
      "project_id": 1,
      "created_at": "2024-01-01T00:00:00Z",
      "last_triggered": "2024-01-01T00:30:00Z",
      "trigger_count": 5
    }
  ]
}
```

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Error description"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to access this resource"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error: Error description"
}
```

---

## Testing the API

### 1. Start the server
```bash
uvicorn app.main:app --reload
```

### 2. Access the interactive documentation
Visit: http://localhost:8000/docs

### 3. Test authentication
```bash
# Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@acme.com", "password": "password123"}'

# Use the returned token for subsequent requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### 4. Test with sample data
The platform includes seeded data for testing:
- Organizations: ACME Corp, TechStart, Research Institute
- Users: admin@acme.com, developer@acme.com, founder@techstart.com, researcher@research.com
- All users have password: `password123` 