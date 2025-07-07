import { useState, useEffect } from 'react';
import { apiClient, Dataset, DatasetItem } from '@/lib/api';

export function useDatasets(projectId: number) {
    const [datasets, setDatasets] = useState<Dataset[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchDatasets = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getProjectDatasets(projectId);

            if (response.error) {
                throw new Error(response.error);
            }

            setDatasets(response.data || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch datasets');
        } finally {
            setIsLoading(false);
        }
    };

    const createDataset = async (datasetData: {
        name: string;
        description?: string;
        project_id: number;
    }) => {
        try {
            const response = await apiClient.createDataset(projectId, datasetData);

            if (response.error) {
                throw new Error(response.error);
            }

            if (response.data) {
                setDatasets(prev => [...prev, response.data]);
                return response.data;
            }

            throw new Error('Failed to create dataset');
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create dataset');
            throw err;
        }
    };

    const uploadFile = async (datasetId: number, file: File) => {
        try {
            const response = await apiClient.uploadDatasetFile(datasetId, file);

            if (response.error) {
                throw new Error(response.error);
            }

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to upload file');
            throw err;
        }
    };

    useEffect(() => {
        if (projectId) {
            fetchDatasets();
        }
    }, [projectId]);

    return {
        datasets,
        isLoading,
        error,
        createDataset,
        uploadFile,
        refetch: fetchDatasets,
    };
}

export function useDatasetItems(datasetId: number, limit: number = 100, offset: number = 0) {
    const [items, setItems] = useState<DatasetItem[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [hasMore, setHasMore] = useState(true);

    const fetchItems = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await apiClient.getDatasetItems(datasetId, limit, offset);

            if (response.error) {
                throw new Error(response.error);
            }

            const newItems = response.data || [];
            setItems(prev => offset === 0 ? newItems : [...prev, ...newItems]);
            setHasMore(newItems.length === limit);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch dataset items');
        } finally {
            setIsLoading(false);
        }
    };

    const createItemsBulk = async (items: Array<{
        input_data: Record<string, any>;
        expected_output?: string;
    }>) => {
        try {
            const response = await apiClient.createDatasetItemsBulk(datasetId, items);

            if (response.error) {
                throw new Error(response.error);
            }

            // Refresh the items list
            await fetchItems();

            return response.data;
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to create dataset items');
            throw err;
        }
    };

    const loadMore = async () => {
        if (!hasMore || isLoading) return;

        const newOffset = items.length;
        try {
            const response = await apiClient.getDatasetItems(datasetId, limit, newOffset);

            if (response.error) {
                throw new Error(response.error);
            }

            const newItems = response.data || [];
            setItems(prev => [...prev, ...newItems]);
            setHasMore(newItems.length === limit);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to load more items');
        }
    };

    useEffect(() => {
        if (datasetId) {
            fetchItems();
        }
    }, [datasetId, limit, offset]);

    return {
        items,
        isLoading,
        error,
        hasMore,
        createItemsBulk,
        loadMore,
        refetch: fetchItems,
    };
} 