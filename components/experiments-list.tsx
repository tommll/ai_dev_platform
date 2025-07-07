"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Play, Pause, Archive, Edit, Trash2 } from "lucide-react"
import { useExperiments } from "@/hooks/useExperiments"
import { useExperimentRuns } from "@/hooks/useExperiments"

interface ExperimentsListProps {
    projectId: number
}

export function ExperimentsList({ projectId }: ExperimentsListProps) {
    const { experiments, isLoading, error, createExperiment } = useExperiments(projectId)
    const [selectedExperimentId, setSelectedExperimentId] = useState<number | null>(null)

    // Get runs for the selected experiment
    const { runs, createRun, cancelRun } = useExperimentRuns(selectedExperimentId || 0)

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'active':
                return 'bg-green-500'
            case 'paused':
                return 'bg-yellow-500'
            case 'archived':
                return 'bg-gray-500'
            default:
                return 'bg-blue-500'
        }
    }

    const handleCreateRun = async (experimentId: number) => {
        try {
            await createRun()
        } catch (error) {
            console.error('Failed to create experiment run:', error)
        }
    }

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
                            <p>Error loading experiments: {error}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    if (experiments.length === 0) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center text-gray-500">
                            <p>No experiments found. Create your first experiment to get started.</p>
                            <Button className="mt-4">Create Experiment</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    return (
        <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Experiments</h2>
                <Button>Create New Experiment</Button>
            </div>

            <div className="grid gap-4">
                {experiments.map((experiment) => (
                    <Card key={experiment.id} className="hover:shadow-md transition-shadow">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="text-lg">{experiment.name}</CardTitle>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {experiment.description || "No description"}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge
                                        variant="outline"
                                        className={`${getStatusColor(experiment.status)} text-white`}
                                    >
                                        {experiment.status}
                                    </Badge>
                                    <div className="flex items-center gap-1">
                                        <Button variant="ghost" size="sm">
                                            <Edit className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Trash2 className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </div>
                            </div>
                        </CardHeader>
                        <CardContent>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                                <div>
                                    <span className="text-muted-foreground">Prompt ID:</span>
                                    <span className="ml-2 font-medium">{experiment.prompt_id}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Dataset ID:</span>
                                    <span className="ml-2 font-medium">{experiment.dataset_id}</span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Created:</span>
                                    <span className="ml-2 font-medium">
                                        {new Date(experiment.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="mt-4 flex items-center gap-2">
                                <Button
                                    size="sm"
                                    onClick={() => handleCreateRun(experiment.id)}
                                    disabled={experiment.status === 'archived'}
                                >
                                    <Play className="w-4 h-4 mr-2" />
                                    Run Experiment
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={experiment.status === 'archived'}
                                >
                                    <Pause className="w-4 h-4 mr-2" />
                                    Pause
                                </Button>
                                <Button
                                    variant="outline"
                                    size="sm"
                                    disabled={experiment.status === 'archived'}
                                >
                                    <Archive className="w-4 h-4 mr-2" />
                                    Archive
                                </Button>
                            </div>

                            {/* Show recent runs if any */}
                            {runs.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-medium mb-2">Recent Runs</h4>
                                    <div className="space-y-2">
                                        {runs.slice(0, 3).map((run) => (
                                            <div key={run.id} className="flex items-center justify-between text-sm">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${run.status === 'completed' ? 'bg-green-500' :
                                                            run.status === 'running' ? 'bg-blue-500' :
                                                                run.status === 'failed' ? 'bg-red-500' :
                                                                    'bg-gray-500'
                                                        }`} />
                                                    <span>{run.run_id}</span>
                                                </div>
                                                <div className="flex items-center gap-4">
                                                    <span className="text-muted-foreground">
                                                        {run.completed_items}/{run.total_items}
                                                    </span>
                                                    <span className="text-muted-foreground">
                                                        {new Date(run.created_at).toLocaleDateString()}
                                                    </span>
                                                    {run.status === 'running' && (
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => cancelRun(run.id)}
                                                        >
                                                            Cancel
                                                        </Button>
                                                    )}
                                                </div>
                                            </div>
                                        ))}
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