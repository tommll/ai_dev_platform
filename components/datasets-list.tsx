"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit, Trash2, Upload, Eye, Download } from "lucide-react"
import { useDatasets } from "@/hooks/useDatasets"
import { useDatasetItems } from "@/hooks/useDatasets"

interface DatasetsListProps {
    projectId: number
}

export function DatasetsList({ projectId }: DatasetsListProps) {
    const { datasets, isLoading, error, createDataset, uploadFile } = useDatasets(projectId)
    const [selectedDatasetId, setSelectedDatasetId] = useState<number | null>(null)

    // Get items for the selected dataset
    const { items, createItemsBulk, loadMore, hasMore } = useDatasetItems(selectedDatasetId || 0)

    if (isLoading) {
        return (
            <div className="p-6">
                <div className="animate-pulse space-y-4">
                    {[1, 2, 3].map((i) => (
                        <Card key={i}>
                            <CardHeader>
                                <div className="h-4 bg-gray-200 rounded w-1/4"></div>
                                <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                            </CardHeader>
                            <CardContent>
                                <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        )
    }

    if (error) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center text-red-600">
                            <p>Error loading datasets: {error}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    if (datasets.length === 0) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center text-gray-500">
                            <p>No datasets found. Create your first dataset to get started.</p>
                            <Button className="mt-4">Create Dataset</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    return (
        <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Datasets</h2>
                <Button>Create New Dataset</Button>
            </div>

            <div className="grid gap-4">
                {datasets.map((dataset) => (
                    <Card key={dataset.id} className="hover:shadow-md transition-shadow">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="text-lg">{dataset.name}</CardTitle>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {dataset.description || "No description"}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge
                                        variant={dataset.is_active ? "default" : "outline"}
                                        className={dataset.is_active ? "bg-green-500" : ""}
                                    >
                                        {dataset.is_active ? "Active" : "Inactive"}
                                    </Badge>
                                    <div className="flex items-center gap-1">
                                        <Button variant="ghost" size="sm">
                                            <Eye className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Edit className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Download className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-muted-foreground">Status:</span>
                                    <span className="ml-2 font-medium">
                                        {dataset.is_active ? "Active" : "Inactive"}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Created:</span>
                                    <span className="ml-2 font-medium">
                                        {new Date(dataset.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="mt-4 flex items-center gap-2">
                                <Button size="sm">
                                    <Upload className="w-4 h-4 mr-2" />
                                    Upload File
                                </Button>
                                <Button variant="outline" size="sm">
                                    <Edit className="w-4 h-4 mr-2" />
                                    Edit
                                </Button>
                                <Button variant="outline" size="sm">
                                    <Eye className="w-4 h-4 mr-2" />
                                    View Items
                                </Button>
                            </div>

                            {/* Show recent items if any */}
                            {items.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-medium mb-2">Recent Items ({items.length})</h4>
                                    <div className="space-y-2 max-h-32 overflow-y-auto">
                                        {items.slice(0, 5).map((item) => (
                                            <div key={item.id} className="flex items-center justify-between text-sm">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                                                    <span className="truncate max-w-xs">
                                                        {typeof item.input_data === 'string'
                                                            ? item.input_data
                                                            : JSON.stringify(item.input_data).substring(0, 50) + '...'
                                                        }
                                                    </span>
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    {item.expected_output && (
                                                        <span className="text-muted-foreground text-xs">
                                                            Expected: {item.expected_output.substring(0, 20)}...
                                                        </span>
                                                    )}
                                                    <span className="text-muted-foreground text-xs">
                                                        {new Date(item.created_at).toLocaleDateString()}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                        {hasMore && (
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                onClick={loadMore}
                                                className="w-full"
                                            >
                                                Load More...
                                            </Button>
                                        )}
                                    </div>
                                </div>
                            )}
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    )
} 