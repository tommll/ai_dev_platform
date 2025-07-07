"use client"

import { useState } from "react"
import { ArrowLeft, ChevronDown, Filter, MoreHorizontal, Settings, Eye, Lock, BarChart3, LogOut, Play, Clock, CheckCircle, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { ReviewModal, EvaluationResult } from "@/components/review-modal"
import { useAuth } from "@/hooks/useAuth"
import { useExperiments, useExperimentRuns } from "@/hooks/useExperiments"
import { usePrompts } from "@/hooks/usePrompts"
import { useDatasets } from "@/hooks/useDatasets"
import { apiClient } from "@/lib/api"

interface ExperimentDashboardProps {
  onTabChange: (tab: string) => void
  onShowReview: () => void
}

// Mock data for demonstration (in real app, this would come from API)
const experimentData = [
  {
    id: "eval-1",
    input: "do you have to have two license plates in ontario",
    outputs: [
      { model: "one", value: "false", color: "bg-gray-500" },
      { model: "two", value: "True.", color: "bg-purple-500" },
      { model: "three", value: "True. In Ontario, C...", color: "bg-blue-500" },
      { model: "four", value: "false", color: "bg-orange-500" },
    ],
    expected: "true",
    exactMatch: "0.0%",
    levenstein: ["20.0%", "60.0%", "1.8%", "20.0%"],
    duration: ["59.2s", "58.2s", "57.2s", "55s"],
    llm: ["0.2s", "0.2s", "0.2s", "0s"],
  },
  {
    id: "eval-2",
    input: "is carling black label a south african beer",
    outputs: [
      { model: "one", value: "true", color: "bg-gray-500" },
      { model: "two", value: "True", color: "bg-purple-500" },
      { model: "three", value: "True. Carling Blac...", color: "bg-blue-500" },
      { model: "four", value: "true", color: "bg-orange-500" },
    ],
    expected: "false",
    exactMatch: "0.0%",
    levenstein: ["20.0%", "20.0%", "1.9%", "20.0%"],
    duration: ["59.1s", "58.2s", "57.1s", "5.1s"],
    llm: ["0.1s", "", "", ""],
  },
  {
    id: "eval-3",
    input: "were the world trade centers the tallest buildings in america",
    outputs: [
      { model: "one", value: "true", color: "bg-gray-500" },
      { model: "two", value: "False", color: "bg-purple-500" },
      { model: "three", value: "False. While the or...", color: "bg-blue-500" },
      { model: "four", value: "false", color: "bg-orange-500" },
    ],
    expected: "true",
    exactMatch: "100.0%",
    levenstein: ["100.0%", "0.0%", "0.0%", "0.0%"],
    duration: ["59.2s", "58.1s", "57.2s", "5.1s"],
    llm: ["0.1s", "0.1s", "0.1s", "0s"],
  },
  {
    id: "eval-4",
    input: "is a wooly mammoth the same as a",
    outputs: [
      { model: "one", value: "false", color: "bg-gray-500" },
      { model: "two", value: "False", color: "bg-purple-500" },
    ],
    expected: "false",
    exactMatch: "100.0%",
    levenstein: ["100.0%", "0.0%"],
    duration: ["59.1s", "58.1s"],
    llm: ["0.1s", "0.1s"],
  },
]

const scoreMetrics = {
  levenstein: {
    score: "68.00%",
    change: "+1.7%",
    distribution: [
      { value: 51.0, change: "+1.7%", color: "bg-purple-500" },
      { value: 1.85, change: "+66%", color: "bg-blue-500" },
      { value: 52.0, change: "+16%", color: "bg-orange-500" },
    ],
  },
  exactMatch: {
    score: "60.00%",
    change: "+60%",
    distribution: [
      { value: 0.0, change: "+60%", color: "bg-gray-500" },
      { value: 0.0, change: "+60%", color: "bg-purple-500" },
      { value: 40.0, change: "+20%", color: "bg-orange-500" },
    ],
  },
  duration: {
    score: "59.17s",
    change: "+1.00s",
    avgValues: [
      { value: "58.17s", change: "+1.00s" },
      { value: "57.18s", change: "+1.99s" },
      { value: "5.06s", change: "-54.11s" },
    ],
  },
  llmDuration: {
    score: "0.1668s",
    change: "+0.0008s",
    avgValues: [
      { value: "0.1660s", change: "+0.0008s" },
      { value: "0.1712s", change: "-0.0044s" },
    ],
  },
}

export function ExperimentDashboard({ onTabChange, onShowReview }: ExperimentDashboardProps) {
  const { user, logout } = useAuth()
  const [selectedModels, setSelectedModels] = useState(["one", "two", "three", "four"])
  const [diffMode, setDiffMode] = useState(true)
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [currentProjectId, setCurrentProjectId] = useState(1) // Default project ID
  const [selectedExperiment, setSelectedExperiment] = useState<number | null>(null)
  const [viewMode, setViewMode] = useState<'experiments' | 'runs'>('experiments')
  const [evaluationResults, setEvaluationResults] = useState<EvaluationResult[]>([])
  const [selectedRunId, setSelectedRunId] = useState<string>("")
  const [isLoadingResults, setIsLoadingResults] = useState(false)

  // API hooks to fetch real data
  const { experiments, isLoading: experimentsLoading, error: experimentsError, createExperiment } = useExperiments(currentProjectId)
  const { prompts, isLoading: promptsLoading } = usePrompts(currentProjectId)
  // const { datasets, isLoading: datasetsLoading } = useDatasets(currentProjectId)

  // Get runs for selected experiment
  const { runs, isLoading: runsLoading, error: runsError, createRun, cancelRun } = useExperimentRuns(selectedExperiment || 0)

  const handleLogout = () => {
    logout()
  }

  const handleExperimentSelect = (experimentId: number) => {
    setSelectedExperiment(experimentId)
    setViewMode('runs')
  }

  const handleStartRun = async (experimentId: number) => {
    try {
      await createRun()
    } catch (error) {
      console.error('Failed to start experiment run:', error)
    }
  }

  const handleCancelRun = async (runId: string) => {
    try {
      await cancelRun(runId)
    } catch (error) {
      console.error('Failed to cancel experiment run:', error)
    }
  }

  const handleViewResults = async (run: any) => {
    if (!selectedExperiment) return

    setIsLoadingResults(true)
    try {
      const response = await apiClient.getExperimentRunResults(selectedExperiment, run.run_id)
      if (response.data) {
        setEvaluationResults(response.data.evaluation_results || [])
        setSelectedRunId(run.run_id)
        setShowReviewModal(true)
      } else {
        console.error('Failed to fetch evaluation results:', response.error)
      }
    } catch (error) {
      console.error('Error fetching evaluation results:', error)
    } finally {
      setIsLoadingResults(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'running':
        return <Clock className="w-4 h-4 text-blue-500" />
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />
      case 'cancelled':
        return <XCircle className="w-4 h-4 text-gray-500" />
      default:
        return <Clock className="w-4 h-4 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800'
      case 'running':
        return 'bg-blue-100 text-blue-800'
      case 'pending':
        return 'bg-yellow-100 text-yellow-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-black rounded-full" />
              <span className="text-sm text-muted-foreground">
                {user?.organization_id === 1 ? "Acme Corp" : "Organization"} / Model comparison
              </span>
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            </div>
            <nav className="flex items-center gap-6">
              <Button variant="ghost" className="text-sm font-medium">
                Experiments
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground" onClick={() => onTabChange("library")}>
                Library
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground" onClick={() => onTabChange("logs")}>
                Logs
              </Button>
              <Button
                variant="ghost"
                className="text-sm text-muted-foreground"
                onClick={() => onTabChange("playgrounds")}
              >
                Playgrounds
              </Button>
              <Button
                variant="ghost"
                className="text-sm text-muted-foreground"
                onClick={() => onTabChange("configuration")}
              >
                Configuration
              </Button>
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">
                {user?.email}
              </span>
              <Button variant="ghost" size="icon" onClick={handleLogout}>
                <LogOut className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* API Data Status */}
      <div className="px-6 py-3 border-b bg-muted/20">
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <span className="font-medium">API Status:</span>
            {experimentsLoading ? (
              <Badge variant="secondary">Loading experiments...</Badge>
            ) : experimentsError ? (
              <Badge variant="destructive">Error: {experimentsError}</Badge>
            ) : (
              <Badge variant="outline">{experiments.length} experiments</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">Prompts:</span>
            {promptsLoading ? (
              <Badge variant="secondary">Loading...</Badge>
            ) : (
              <Badge variant="outline">{prompts.length} prompts</Badge>
            )}
          </div>
          <div className="flex items-center gap-2">
            <span className="font-medium">Datasets:</span>
            {/* {datasetsLoading ? (
              <Badge variant="secondary">Loading...</Badge>
            ) : (
              <Badge variant="outline">{datasets.length} datasets</Badge>
            )} */}
          </div>
          {selectedExperiment && (
            <div className="flex items-center gap-2">
              <span className="font-medium">Runs:</span>
              {runsLoading ? (
                <Badge variant="secondary">Loading...</Badge>
              ) : runsError ? (
                <Badge variant="destructive">Error: {runsError}</Badge>
              ) : (
                <Badge variant="outline">{runs.length} runs</Badge>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Experiment Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => {
                setSelectedExperiment(null)
                setViewMode('experiments')
              }}
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <h1 className="text-xl font-semibold">
              {viewMode === 'experiments' ? 'Experiments' : 'Experiment Runs'}
            </h1>
            {selectedExperiment && (
              <span className="text-sm text-muted-foreground">
                Experiment ID: {selectedExperiment}
              </span>
            )}
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <BarChart3 className="w-4 h-4" />
              <span>main 58b9549</span>
            </div>
            <Select defaultValue="experiments">
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="experiments">Experiments</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex items-center gap-2">
              <span className="text-sm">Diff</span>
              <Switch checked={diffMode} onCheckedChange={setDiffMode} />
            </div>
            <Button variant="outline" size="sm" onClick={onShowReview}>
              <Eye className="w-4 h-4 mr-2" />
              Review
            </Button>
            <Button variant="outline" size="sm">
              <Lock className="w-4 h-4 mr-2" />
              Private
            </Button>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Controls */}
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <Select defaultValue="all">
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="All rows" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All rows</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Columns
              </Button>
              <Button variant="outline" size="sm">
                <Filter className="w-4 h-4 mr-2" />
                Filter
              </Button>
              <Button variant="outline" size="sm">
                Row height
              </Button>
            </div>
          </div>

          {viewMode === 'experiments' ? (
            /* Experiments List */
            <div className="space-y-4">
              {experimentsLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                  <p className="mt-2 text-sm text-muted-foreground">Loading experiments...</p>
                </div>
              ) : experimentsError ? (
                <div className="text-center py-8">
                  <p className="text-red-500">Error loading experiments: {experimentsError}</p>
                </div>
              ) : experiments.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No experiments found</p>
                </div>
              ) : (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>ID</TableHead>
                        <TableHead>Name</TableHead>
                        <TableHead>Description</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Prompt ID</TableHead>
                        <TableHead>Dataset ID</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {experiments.map((experiment) => (
                        <TableRow key={experiment.id}>
                          <TableCell className="font-medium">{experiment.id}</TableCell>
                          <TableCell>{experiment.name}</TableCell>
                          <TableCell className="max-w-xs truncate">
                            {experiment.description || 'No description'}
                          </TableCell>
                          <TableCell>
                            <Badge variant="outline">{experiment.status}</Badge>
                          </TableCell>
                          <TableCell>{experiment.prompt_id}</TableCell>
                          <TableCell>{experiment.dataset_id}</TableCell>
                          <TableCell>
                            {new Date(experiment.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleExperimentSelect(experiment.id)}
                              >
                                <Eye className="w-4 h-4 mr-1" />
                                View Runs
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleStartRun(experiment.id)}
                              >
                                <Play className="w-4 h-4 mr-1" />
                                Start Run
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          ) : (
            /* Experiment Runs List */
            <div className="space-y-4">
              {runsLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mx-auto"></div>
                  <p className="mt-2 text-sm text-muted-foreground">Loading runs...</p>
                </div>
              ) : runsError ? (
                <div className="text-center py-8">
                  <p className="text-red-500">Error loading runs: {runsError}</p>
                </div>
              ) : runs.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground">No runs found for this experiment</p>
                  <Button
                    className="mt-4"
                    onClick={() => handleStartRun(selectedExperiment!)}
                  >
                    <Play className="w-4 h-4 mr-2" />
                    Start First Run
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Run ID</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Progress</TableHead>
                        <TableHead>Total Items</TableHead>
                        <TableHead>Completed</TableHead>
                        <TableHead>Failed</TableHead>
                        <TableHead>Created</TableHead>
                        <TableHead>Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {runs.map((run) => (
                        <TableRow key={run.id}>
                          <TableCell className="font-medium">{run.run_id}</TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              {getStatusIcon(run.status)}
                              <Badge className={getStatusColor(run.status)}>
                                {run.status}
                              </Badge>
                            </div>
                          </TableCell>
                          <TableCell>
                            {run.total_items > 0 ? (
                              <div className="flex items-center gap-2">
                                <Progress
                                  value={(run.completed_items / run.total_items) * 100}
                                  className="w-20"
                                />
                                <span className="text-sm">
                                  {Math.round((run.completed_items / run.total_items) * 100)}%
                                </span>
                              </div>
                            ) : (
                              <span className="text-sm text-muted-foreground">-</span>
                            )}
                          </TableCell>
                          <TableCell>{run.total_items}</TableCell>
                          <TableCell>{run.completed_items}</TableCell>
                          <TableCell>{run.failed_items}</TableCell>
                          <TableCell>
                            {new Date(run.created_at).toLocaleDateString()}
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleViewResults(run)}
                                disabled={isLoadingResults || run.status !== 'completed'}
                              >
                                <Eye className="w-4 h-4 mr-1" />
                                {isLoadingResults ? 'Loading...' : 'Results'}
                              </Button>
                              {['pending', 'running'].includes(run.status) && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => handleCancelRun(run.id)}
                                >
                                  <XCircle className="w-4 h-4 mr-1" />
                                  Cancel
                                </Button>
                              )}
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Scores Sidebar */}
        <div className="w-80 border-l bg-muted/20 p-6">
          <h2 className="font-semibold mb-4 flex items-center justify-between">
            {viewMode === 'experiments' ? 'Experiments Summary' : 'Run Summary'}
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
          </h2>

          {viewMode === 'experiments' ? (
            /* Experiments Summary */
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Total Experiments</span>
                </div>
                <div className="text-2xl font-bold">{experiments.length}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {experiments.filter(e => e.status === 'active').length} active
                </div>
              </div>

              <Separator />

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Status Distribution</span>
                </div>
                <div className="space-y-2">
                  {['draft', 'active', 'completed', 'failed'].map(status => {
                    const count = experiments.filter(e => e.status === status).length
                    const percentage = experiments.length > 0 ? (count / experiments.length) * 100 : 0
                    return (
                      <div key={status} className="flex items-center justify-between">
                        <span className="text-sm capitalize">{status}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={percentage} className="w-16 h-2" />
                          <span className="text-sm">{count}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>
            </div>
          ) : (
            /* Runs Summary */
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Total Runs</span>
                </div>
                <div className="text-2xl font-bold">{runs.length}</div>
                <div className="text-sm text-muted-foreground mt-1">
                  {runs.filter(r => r.status === 'completed').length} completed
                </div>
              </div>

              <Separator />

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Status Distribution</span>
                </div>
                <div className="space-y-2">
                  {['pending', 'running', 'completed', 'failed', 'cancelled'].map(status => {
                    const count = runs.filter(r => r.status === status).length
                    const percentage = runs.length > 0 ? (count / runs.length) * 100 : 0
                    return (
                      <div key={status} className="flex items-center justify-between">
                        <span className="text-sm capitalize">{status}</span>
                        <div className="flex items-center gap-2">
                          <Progress value={percentage} className="w-16 h-2" />
                          <span className="text-sm">{count}</span>
                        </div>
                      </div>
                    )
                  })}
                </div>
              </div>

              {runs.length > 0 && (
                <>
                  <Separator />
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium">Average Metrics</span>
                    </div>
                    <div className="space-y-2">
                      {runs.filter(r => r.metrics).length > 0 && (
                        <div className="text-sm">
                          <div className="flex justify-between">
                            <span>Accuracy:</span>
                            <span>
                              {(runs.filter(r => r.metrics?.accuracy).reduce((sum, r) => sum + (r.metrics?.accuracy || 0), 0) / runs.filter(r => r.metrics?.accuracy).length * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className="flex justify-between">
                            <span>Avg Latency:</span>
                            <span>
                              {(runs.filter(r => r.metrics?.latency).reduce((sum, r) => sum + (r.metrics?.latency || 0), 0) / runs.filter(r => r.metrics?.latency).length).toFixed(0)}ms
                            </span>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </>
              )}
            </div>
          )}
        </div>
      </div>
      <ReviewModal
        open={showReviewModal}
        onOpenChange={setShowReviewModal}
        evaluationResults={evaluationResults}
        runId={selectedRunId}
      />
    </div>
  )
}
