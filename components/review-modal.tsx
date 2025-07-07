"use client"

import { useState, useEffect } from "react"
import { X, ChevronLeft, ChevronRight, ChevronDown, Link } from "lucide-react"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"

export interface EvaluationResult {
  metrics: Record<string, any>
  input_data: Record<string, any>
  expected_output: string
  actual_output: string
  accuracy_score: number
  latency_ms: number
  cost_usd: number
  custom_metrics: Record<string, any>
  created_at: string
  started_at: string | null
  completed_at: string | null
}

export interface ReviewModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  evaluationResults?: EvaluationResult[]
  runId?: string
}

export function ReviewModal({ open, onOpenChange, evaluationResults = [], runId }: ReviewModalProps) {
  const [selectedScores, setSelectedScores] = useState<Record<string, boolean>>({})
  const [currentScore, setCurrentScore] = useState<string>("")
  const [scoreValue, setScoreValue] = useState<string | null>(null)
  const [autoAdvance, setAutoAdvance] = useState(false)
  const [currentRow, setCurrentRow] = useState(1)

  // Generate scores from evaluation results metrics
  const scores = evaluationResults.length > 0 && evaluationResults[0].metrics
    ? Object.keys(evaluationResults[0].metrics).map(key => ({
      id: key,
      label: key.replace(/_/g, ' '),
      checked: false
    }))
    : []

  // Initialize selected scores
  useEffect(() => {
    const initialScores = scores.reduce((acc, score) => ({ ...acc, [score.id]: score.checked }), {})
    setSelectedScores(initialScores)
    if (scores.length > 0) {
      setCurrentScore(scores[0].id)
    }
  }, [evaluationResults])

  const totalRows = evaluationResults.length
  const currentResult = evaluationResults[currentRow - 1]

  const handleScoreSelect = (score: string) => {
    setScoreValue(score)
  }

  const handlePreviousRow = () => {
    if (currentRow > 1) {
      setCurrentRow(currentRow - 1)
      setScoreValue(null)
    }
  }

  const handleNextRow = () => {
    if (currentRow < totalRows) {
      setCurrentRow(currentRow + 1)
      setScoreValue(null)
    }
  }

  // If no evaluation results, show empty state
  if (evaluationResults.length === 0) {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="max-w-2xl">
          <div className="flex items-center justify-between p-4 border-b">
            <h2 className="text-lg font-semibold">Human review</h2>
            <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="p-6 text-center">
            <p className="text-muted-foreground">No evaluation results available for review.</p>
          </div>
        </DialogContent>
      </Dialog>
    )
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl max-h-[95vh] p-0 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">Human review</h2>
            <span className="text-sm text-muted-foreground font-mono">{runId || 'No Run ID'}</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span>Row</span>
              <span className="font-medium">{currentRow}</span>
              <span className="text-muted-foreground">of {totalRows}</span>
            </div>
            <Button variant="outline" size="sm" onClick={handlePreviousRow} disabled={currentRow === 1}>
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous row
            </Button>
            <Button variant="outline" size="sm" onClick={handleNextRow} disabled={currentRow === totalRows}>
              Next row
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
            <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>

        <div className="flex flex-1 overflow-hidden">
          {/* Left Sidebar - Score Selection */}
          <div className="w-48 border-r bg-muted/20 p-4">
            <h3 className="font-medium mb-3">Select score</h3>
            <div className="space-y-2">
              {scores.map((score) => (
                <div key={score.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={score.id}
                    checked={selectedScores[score.id] || false}
                    onCheckedChange={(checked) => setSelectedScores((prev) => ({ ...prev, [score.id]: checked === true }))}
                  />
                  <label
                    htmlFor={score.id}
                    className={`text-sm cursor-pointer ${score.id === currentScore ? "font-medium" : ""}`}
                  >
                    {score.label}
                  </label>
                </div>
              ))}
            </div>
          </div>

          {/* Center - Scoring Interface */}
          <div className="flex-1 p-6">
            <div className="space-y-6">
              {/* Score Navigation */}
              <div className="flex items-center justify-between">
                <Button variant="outline" size="sm">
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Previous score
                </Button>
                <Button variant="outline" size="sm">
                  Next score
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>

              {/* Current Score */}
              {currentScore && (
                <div>
                  <h2 className="text-xl font-semibold mb-4">{currentScore.replace(/_/g, ' ')}</h2>
                  <div className="flex items-center gap-3">
                    <Button
                      variant={scoreValue === "good" ? "default" : "outline"}
                      onClick={() => handleScoreSelect("good")}
                      className="bg-blue-100 hover:bg-blue-200 text-blue-900 border-blue-300"
                    >
                      good <span className="ml-1 text-xs">1</span>
                    </Button>
                    <Button
                      variant={scoreValue === "bad" ? "default" : "outline"}
                      onClick={() => handleScoreSelect("bad")}
                      className="bg-red-100 hover:bg-red-200 text-red-900 border-red-300"
                    >
                      bad <span className="ml-1 text-xs">2</span>
                    </Button>
                    <Button
                      variant={scoreValue === "neutral" ? "default" : "outline"}
                      onClick={() => handleScoreSelect("neutral")}
                      className="bg-gray-100 hover:bg-gray-200 text-gray-900 border-gray-300"
                    >
                      neutral <span className="ml-1 text-xs">3</span>
                    </Button>
                  </div>
                </div>
              )}

              {/* Keyboard Shortcuts */}
              <div className="mt-12">
                <h3 className="text-sm font-medium text-muted-foreground mb-3">Keyboard shortcuts</h3>
                <div className="space-y-2 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono">
                      0
                    </Badge>
                    <span>-</span>
                    <Badge variant="outline" className="font-mono">
                      9
                    </Badge>
                    <span>Set score value</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono">
                      ↑
                    </Badge>
                    <Badge variant="outline" className="font-mono">
                      ↓
                    </Badge>
                    <span>Go to previous or next score</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline" className="font-mono">
                      ←
                    </Badge>
                    <Badge variant="outline" className="font-mono">
                      →
                    </Badge>
                    <span>Go to previous or next row</span>
                  </div>
                </div>

                <div className="flex items-center gap-2 mt-4">
                  <Switch id="auto-advance" checked={autoAdvance} onCheckedChange={setAutoAdvance} />
                  <label htmlFor="auto-advance" className="text-sm text-muted-foreground">
                    Auto-advance
                  </label>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Move to next score/row when using keyboard to set score
                </p>
              </div>

              {/* Configure Scores Link */}
              <div className="mt-8">
                <Button variant="link" className="p-0 h-auto text-blue-600">
                  Configure scores
                </Button>
              </div>
            </div>
          </div>

          {/* Right Sidebar - Span Details */}
          <div className="w-96 border-l bg-muted/20">
            <ScrollArea className="h-full">
              <div className="p-4 space-y-6">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <h3 className="font-medium">Span details</h3>
                  <Button variant="ghost" size="icon">
                    <Link className="w-4 h-4" />
                  </Button>
                </div>

                {/* Scores */}
                {currentResult && currentResult.metrics && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Scores</h4>
                      <ChevronDown className="w-4 h-4" />
                    </div>
                    <div className="space-y-3">
                      {Object.entries(currentResult.metrics).map(([key, value]) => (
                        <div key={key} className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">{key.replace(/_/g, ' ')}</span>
                          <span className="text-sm font-medium">
                            {typeof value === 'number' ? `${(value * 100).toFixed(2)}%` : String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <Separator />

                {/* Input */}
                {currentResult && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Input</h4>
                      <ChevronDown className="w-4 h-4" />
                    </div>
                    <div className="mb-2">
                      <Badge variant="secondary">JSON</Badge>
                      <ChevronDown className="w-4 h-4 ml-1 inline" />
                    </div>
                    <div className="text-sm bg-muted p-3 rounded font-mono text-xs">
                      {JSON.stringify(currentResult.input_data, null, 2)}
                    </div>
                  </div>
                )}

                <Separator />

                {/* Output */}
                {currentResult && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Output</h4>
                      <ChevronDown className="w-4 h-4" />
                    </div>
                    <div className="mb-2">
                      <Badge variant="secondary">Text</Badge>
                      <ChevronDown className="w-4 h-4 ml-1 inline" />
                    </div>
                    <div className="text-sm leading-relaxed">{currentResult.actual_output}</div>
                  </div>
                )}

                <Separator />

                {/* Expected */}
                {currentResult && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Expected</h4>
                      <ChevronDown className="w-4 h-4" />
                    </div>
                    <div className="mb-2">
                      <Badge variant="secondary">Text</Badge>
                      <ChevronDown className="w-4 h-4 ml-1 inline" />
                    </div>
                    <div className="bg-muted p-3 rounded text-sm font-mono">
                      <div className="text-blue-600 mb-1">1</div>
                      <div className="pl-4">{currentResult.expected_output}</div>
                    </div>
                  </div>
                )}

                <Separator />

                {/* Metrics */}
                {currentResult && (
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h4 className="font-medium">Metrics</h4>
                      <ChevronDown className="w-4 h-4" />
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Accuracy Score:</span>
                        <span className="font-medium">{(currentResult.accuracy_score * 100).toFixed(2)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Latency:</span>
                        <span className="font-medium">{currentResult.latency_ms.toFixed(2)}ms</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Cost:</span>
                        <span className="font-medium">${currentResult.cost_usd.toFixed(4)}</span>
                      </div>
                    </div>
                  </div>
                )}

                <Separator />

                {/* Metadata */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Metadata</h4>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  {currentResult && (
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Created:</span>
                        <span>{new Date(currentResult.created_at).toLocaleString()}</span>
                      </div>
                      {currentResult.started_at && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Started:</span>
                          <span>{new Date(currentResult.started_at).toLocaleString()}</span>
                        </div>
                      )}
                      {currentResult.completed_at && (
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Completed:</span>
                          <span>{new Date(currentResult.completed_at).toLocaleString()}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </ScrollArea>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default ReviewModal

