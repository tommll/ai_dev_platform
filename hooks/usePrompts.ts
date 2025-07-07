import { useState, useEffect } from 'react';
import { apiClient, Prompt, PromptVersion } from '@/lib/api';

export function usePrompts(projectId: number) {
    const [prompts, setPrompts] = useState<Prompt[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchPrompts = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getProjectPrompts(projectId);

            if (response.error) {
                throw new Error(response.error);
            }

            setPrompts(response.data || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch prompts');
        } finally {
            setIsLoading(false);
        }
    };

    const createPrompt = async (promptData: {
        name: string;
        description?: string;
        project_id: number;
    }) => {
        try {
            const response = await apiClient.createPrompt(projectId, promptData);

            if (response.error) {
                throw new Error(response.error);
            }

            if (response.data) {
                setPrompts(prev => [...prev, response.data]);
                return response.data;
            }

            throw new Error('Failed to create prompt');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create prompt');
            throw err;
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchPrompts();
        }
    }, [projectId]);

    return {
        prompts,
        isLoading,
        error,
        createPrompt,
        refetch: fetchPrompts,
    };
}

export function usePromptVersions(promptId: number) {
    const [versions, setVersions] = useState<PromptVersion[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchVersions = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getPromptVersions(promptId);

            if (response.error) {
                throw new Error(response.error);
            }

            setVersions(response.data || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch prompt versions');
        } finally {
            setIsLoading(false);
        }
    };

    const createVersion = async (versionData: {
        version: string;
        template: string;
        variables?: Record<string, any>;
        prompt_id: number;
    }) => {
        try {
            const response = await apiClient.createPromptVersion(promptId, versionData);

            if (response.error) {
                throw new Error(response.error);
            }

            if (response.data) {
                setVersions(prev => [...prev, response.data]);
                return response.data;
            }

            throw new Error('Failed to create prompt version');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create prompt version');
            throw err;
        }
    };

    const deployVersion = async (version: string) => {
        try {
            const response = await apiClient.deployPromptVersion(promptId, version);

            if (response.error) {
                throw new Error(response.error);
            }

            // Update the versions to reflect the deployment
            setVersions(prev => prev.map(v => ({
                ...v,
                is_deployed: v.version === version
            })));

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to deploy prompt version');
            throw err;
        }
    };

    useEffect(() => {
        if (promptId) {
            fetchVersions();
        }
    }, [promptId]);

    return {
        versions,
        isLoading,
        error,
        createVersion,
        deployVersion,
        refetch: fetchVersions,
    };
} 