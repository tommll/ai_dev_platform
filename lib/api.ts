// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// Types for API responses
export interface ApiResponse<T = any> {
    data?: T;
    error?: string;
    message?: string;
}

export interface LoginRequest {
    email: string;
    password: string;
}

export interface LoginResponse {
    access_token: string;
    token_type: string;
    expires_in: number;
}

export interface User {
    id: number;
    email: string;
    username: string;
    full_name: string | null;
    is_active: boolean;
    is_superuser: boolean;
    organization_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface Project {
    id: number;
    name: string;
    description: string | null;
    is_active: boolean;
    organization_id: number;
    owner_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface Prompt {
    id: number;
    name: string;
    description: string | null;
    is_active: boolean;
    is_deployed: boolean;
    project_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface PromptVersion {
    id: number;
    version: string;
    template: string;
    variables: Record<string, any> | null;
    is_deployed: boolean;
    prompt_id: number;
    created_at: string;
}

export interface Dataset {
    id: number;
    name: string;
    description: string | null;
    is_active: boolean;
    project_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface DatasetItem {
    id: number;
    input_data: Record<string, any>;
    expected_output: string | null;
    dataset_id: number;
    created_at: string;
}

export interface Experiment {
    id: number;
    name: string;
    description: string | null;
    status: 'draft' | 'active' | 'paused' | 'archived';
    prompt_id: number;
    dataset_id: number;
    model_configuration: Record<string, any>;
    evaluation_config: Record<string, any>;
    project_id: number;
    created_at: string;
    updated_at: string | null;
}

export interface ExperimentRun {
    id: string;
    run_id: string;
    status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
    total_items: number;
    completed_items: number;
    failed_items: number;
    metrics: Record<string, any> | null;
    experiment_id: number;
    created_at: string;
    started_at: string | null;
    completed_at: string | null;
}

export interface Trace {
    trace_id: string;
    prompt_id: number;
    input_data: Record<string, any>;
    output_data: Record<string, any> | null;
    latency_ms: number | null;
    tokens_used: number | null;
    cost_usd: number | null;
    model_name: string | null;
    model_provider: string | null;
    is_success: boolean;
    error_message: string | null;
}

// API Client Class
class ApiClient {
    private baseURL: string;
    private token: string | null = null;

    constructor(baseURL: string = API_BASE_URL) {
        this.baseURL = baseURL;
        // Try to get token from localStorage on initialization
        if (typeof window !== 'undefined') {
            this.token = localStorage.getItem('auth_token');
        }
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<ApiResponse<T>> {
        const url = `${this.baseURL}${endpoint}`;

        const headers: HeadersInit = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return {
                error: error instanceof Error ? error.message : 'An unknown error occurred',
            };
        }
    }

    // Authentication methods
    setToken(token: string) {
        this.token = token;
        if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', token);
        }
    }

    clearToken() {
        this.token = null;
        if (typeof window !== 'undefined') {
            localStorage.removeItem('auth_token');
        }
    }

    async login(credentials: LoginRequest): Promise<ApiResponse<LoginResponse>> {
        const response = await this.request<LoginResponse>('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials),
        });

        if (response.data) {
            this.setToken(response.data.access_token);
        }

        return response;
    }

    async logout() {
        this.clearToken();
    }

    // User methods
    async getCurrentUser(): Promise<ApiResponse<User>> {
        return this.request<User>('/users/me');
    }

    async updateUserPreferences(updates: Partial<User>): Promise<ApiResponse<User>> {
        return this.request<User>('/users/me/preferences', {
            method: 'PUT',
            body: JSON.stringify(updates),
        });
    }

    async getOrganizationMembers(organizationId: number): Promise<ApiResponse<{
        organization: { id: number; name: string; slug: string };
        members: User[];
    }>> {
        return this.request(`/organizations/${organizationId}/members`);
    }

    // Project methods
    async getProjects(): Promise<ApiResponse<Project[]>> {
        // Note: This endpoint doesn't exist in the current API, but would be useful
        return this.request<Project[]>('/projects');
    }

    // Prompt methods
    async getProjectPrompts(projectId: number): Promise<ApiResponse<Prompt[]>> {
        return this.request<Prompt[]>(`/projects/${projectId}/prompts`);
    }

    async createPrompt(projectId: number, promptData: {
        name: string;
        description?: string;
        project_id: number;
    }): Promise<ApiResponse<Prompt>> {
        return this.request<Prompt>(`/projects/${projectId}/prompts`, {
            method: 'POST',
            body: JSON.stringify(promptData),
        });
    }

    async getPromptVersions(promptId: number): Promise<ApiResponse<PromptVersion[]>> {
        return this.request<PromptVersion[]>(`/prompts/${promptId}/versions`);
    }

    async createPromptVersion(promptId: number, versionData: {
        version: string;
        template: string;
        variables?: Record<string, any>;
        prompt_id: number;
    }): Promise<ApiResponse<PromptVersion>> {
        return this.request<PromptVersion>(`/prompts/${promptId}/versions`, {
            method: 'POST',
            body: JSON.stringify(versionData),
        });
    }

    async deployPromptVersion(promptId: number, version: string): Promise<ApiResponse<{
        message: string;
        prompt_id: number;
        version: string;
    }>> {
        return this.request(`/prompts/${promptId}/versions/${version}/deploy`, {
            method: 'PUT',
        });
    }

    // Dataset methods
    async getProjectDatasets(projectId: number): Promise<ApiResponse<Dataset[]>> {
        return this.request<Dataset[]>(`/projects/${projectId}/datasets`);
    }

    async createDataset(projectId: number, datasetData: {
        name: string;
        description?: string;
        project_id: number;
    }): Promise<ApiResponse<Dataset>> {
        return this.request<Dataset>(`/projects/${projectId}/datasets`, {
            method: 'POST',
            body: JSON.stringify(datasetData),
        });
    }

    async uploadDatasetFile(datasetId: number, file: File): Promise<ApiResponse<{
        message: string;
        dataset_id: number;
        items_created: number;
    }>> {
        const formData = new FormData();
        formData.append('file', file);

        const url = `${this.baseURL}/datasets/${datasetId}/upload`;
        const headers: HeadersInit = {};

        if (this.token) {
            headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers,
                body: formData,
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return { data };
        } catch (error) {
            return {
                error: error instanceof Error ? error.message : 'An unknown error occurred',
            };
        }
    }

    async getDatasetItems(
        datasetId: number,
        limit: number = 100,
        offset: number = 0
    ): Promise<ApiResponse<DatasetItem[]>> {
        return this.request<DatasetItem[]>(
            `/datasets/${datasetId}/items?limit=${limit}&offset=${offset}`
        );
    }

    async createDatasetItemsBulk(
        datasetId: number,
        items: Array<{
            input_data: Record<string, any>;
            expected_output?: string;
        }>
    ): Promise<ApiResponse<{
        message: string;
        dataset_id: number;
        items_created: number;
    }>> {
        return this.request(`/datasets/${datasetId}/items/bulk`, {
            method: 'POST',
            body: JSON.stringify({ items }),
        });
    }

    // Experiment methods
    async getProjectExperiments(projectId: number): Promise<ApiResponse<Experiment[]>> {
        return this.request<Experiment[]>(`/experiments?project_id=${projectId}`);
    }
    async createExperiment(experimentData: {
        name: string;
        description?: string;
        prompt_id: number;
        dataset_id: number;
        model_configuration: Record<string, any>;
        evaluation_config: Record<string, any>;
        project_id: number;
    }): Promise<ApiResponse<Experiment>> {
        return this.request<Experiment>('/experiments', {
            method: 'POST',
            body: JSON.stringify(experimentData),
        });
    }

    async createExperimentRun(
        experimentId: number,
        runData: { experiment_id: number }
    ): Promise<ApiResponse<ExperimentRun>> {
        return this.request<ExperimentRun>(`/experiments/${experimentId}/runs`, {
            method: 'POST',
            body: JSON.stringify(runData),
        });
    }

    async getExperimentRunStatus(
        experimentId: number,
        runId: string
    ): Promise<ApiResponse<{
        run_id: string;
        status: string;
        total_items: number;
        completed_items: number;
        failed_items: number;
        progress_percentage: number;
        created_at: string;
        started_at: string | null;
        completed_at: string | null;
    }>> {
        return this.request(`/experiments/${experimentId}/runs/${runId}/status`);
    }

    async getExperimentRuns(experimentId: number): Promise<ApiResponse<ExperimentRun[]>> {
        return this.request<ExperimentRun[]>(`/experiments/${experimentId}/runs`, {
            method: 'GET',
        });
    }

    async getExperimentRunResults(
        experimentId: number,
        runId: string
    ): Promise<ApiResponse<{
        run_id: string;
        status: string;
        metrics: Record<string, any>;
        total_items: number;
        completed_items: number;
        failed_items: number;
        evaluation_results: Array<{
            id: number;
            dataset_item_id: number;
            input_data: Record<string, any>;
            output_data: Record<string, any>;
            metrics: Record<string, any>;
            is_success: boolean;
            error_message: string | null;
            created_at: string;
        }>;
        created_at: string;
        started_at: string | null;
        completed_at: string | null;
    }>> {
        return this.request(`/experiments/${experimentId}/runs/${runId}/results`);
    }

    async cancelExperimentRun(
        experimentId: number,
        runId: string
    ): Promise<ApiResponse<{
        message: string;
        run_id: string;
        status: string;
    }>> {
        return this.request(`/experiments/${experimentId}/runs/${runId}/cancel`, {
            method: 'POST',
        });
    }

    // Observability methods
    async submitTrace(traceData: Trace): Promise<ApiResponse<{
        trace_id: string;
        message: string;
    }>> {
        return this.request('/traces', {
            method: 'POST',
            body: JSON.stringify(traceData),
        });
    }

    async queryMetrics(
        projectId: number,
        metricType: 'eval' | 'trace' | 'usage',
        params: {
            start_time?: string;
            end_time?: string;
            interval?: string;
        } = {}
    ): Promise<ApiResponse<{ metrics: any[] }>> {
        const searchParams = new URLSearchParams({
            metric_type: metricType,
            ...params,
        });

        return this.request(`/projects/${projectId}/metrics?${searchParams}`);
    }

    async createAlertRule(
        projectId: number,
        alertData: {
            name: string;
            description?: string;
            metric_name: string;
            threshold: number;
            operator: string;
            time_window_minutes: number;
            is_active: boolean;
        }
    ): Promise<ApiResponse<any>> {
        return this.request(`/projects/${projectId}/alerts`, {
            method: 'POST',
            body: JSON.stringify(alertData),
        });
    }

    async getProjectAlerts(projectId: number): Promise<ApiResponse<{
        alerts: any[];
    }>> {
        return this.request(`/projects/${projectId}/alerts`);
    }
}

// Create and export a singleton instance
export const apiClient = new ApiClient();

// Export types
export type {
    LoginRequest,
    LoginResponse,
    User,
    Project,
    Prompt,
    PromptVersion,
    Dataset,
    DatasetItem,
    Experiment,
    ExperimentRun,
    Trace,
}; 