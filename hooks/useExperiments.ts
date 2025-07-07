import { useState, useEffect } from 'react';
import { apiClient, Experiment, ExperimentRun } from '@/lib/api';

export function useExperiments(projectId: number) {
    const [experiments, setExperiments] = useState<Experiment[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchExperiments = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getProjectExperiments(projectId);
            if (response.error) {
                throw new Error(response.error);
            }
            setExperiments(response.data || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch experiments');
        } finally {
            setIsLoading(false);
        }
    };

    const createExperiment = async (experimentData: {
        name: string;
        description?: string;
        prompt_id: number;
        dataset_id: number;
        model_configuration: Record<string, any>;
        evaluation_config: Record<string, any>;
        project_id: number;
    }) => {
        try {
            const response = await apiClient.createExperiment(experimentData);

            if (response.error) {
                throw new Error(response.error);
            }

            if (response.data) {
                setExperiments(prev => [...prev, response.data]);
                return response.data;
            }

            throw new Error('Failed to create experiment');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create experiment');
            throw err;
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchExperiments();
        }
    }, [projectId]);

    return {
        experiments,
        isLoading,
        error,
        createExperiment,
        refetch: fetchExperiments,
    };
}

export function useExperimentRuns(experimentId: number) {
    const [runs, setRuns] = useState<ExperimentRun[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchRuns = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getExperimentRuns(experimentId);
            if (response.error) {
                throw new Error(response.error);
            }
            setRuns(response.data || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch runs');
        } finally {
            setIsLoading(false);
        }
    };

    const createRun = async () => {
        try {
            const response = await apiClient.createExperimentRun(experimentId, {
                experiment_id: experimentId
            });

            if (response.error) {
                throw new Error(response.error);
            }

            if (response.data) {
                setRuns(prev => [...prev, response.data]);
                return response.data;
            }

            throw new Error('Failed to create experiment run');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create experiment run');
            throw err;
        }
    };

    const getRunStatus = async (runId: string) => {
        try {
            const response = await apiClient.getExperimentRunStatus(experimentId, runId);

            if (response.error) {
                throw new Error(response.error);
            }

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to get run status');
            throw err;
        }
    };

    const getRunResults = async (runId: string) => {
        try {
            const response = await apiClient.getExperimentRunResults(experimentId, runId);

            if (response.error) {
                throw new Error(response.error);
            }

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to get run results');
            throw err;
        }
    };

    const cancelRun = async (runId: string) => {
        try {
            const response = await apiClient.cancelExperimentRun(experimentId, runId);

            if (response.error) {
                throw new Error(response.error);
            }

            // Update the run status in local state
            setRuns(prev => prev.map(run =>
                run.id === runId
                    ? { ...run, status: 'cancelled' as const }
                    : run
            ));

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to cancel run');
            throw err;
        }
    };

    useEffect(() => {
        if (experimentId) {
            fetchRuns();
        }
    }, [experimentId]);

    return {
        runs,
        isLoading,
        error,
        createRun,
        getRunStatus,
        getRunResults,
        cancelRun,
        refetch: fetchRuns,
    };
}

export function useExperimentRunStatus(experimentId: number, runId: string) {
    const [status, setStatus] = useState<any>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchStatus = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getExperimentRunStatus(experimentId, runId);

            if (response.error) {
                throw new Error(response.error);
            }

            setStatus(response.data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch run status');
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        if (experimentId && runId) {
            fetchStatus();

            // Poll for status updates if run is still active
            const interval = setInterval(() => {
                if (status && ['pending', 'running'].includes(status.status)) {
                    fetchStatus();
                }
            }, 5000); // Poll every 5 seconds

            return () => clearInterval(interval);
        }
    }, [experimentId, runId]);

    return {
        status,
        isLoading,
        error,
        refetch: fetchStatus,
    };
} 