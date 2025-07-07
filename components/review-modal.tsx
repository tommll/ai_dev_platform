"use client"

import { useState } from "react"
import { X, ChevronLeft, ChevronRight, ChevronDown, Link } from "lucide-react"
import { Dialog, DialogContent } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Switch } from "@/components/ui/switch"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"

export interface ReviewModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const reviewData = {
  id: "a7be934f-1812-4dfb-961f-619e3e452689",
  currentRow: 1,
  totalRows: 20,
  scores: [
    { id: "another_score", label: "another score", checked: false },
    { id: "response_quality", label: "response quality", checked: true },
  ],
  currentScore: "response_quality",
  scoreValues: {
    response_quality: {
      good: 1,
      bad: 2,
      neutral: 3,
      selected: null,
    },
  },
  spanDetails: {
    scores: {
      factuality: "0.00%",
      avg_relevance: "80.00%",
      max_relevance: "80.00%",
      min_relevance: "80.00%",
      factuality_parsed: "100.00%",
    },
    input: "What happens when I star a doc?",
    output: `When you star a doc, it is saved to your personal "My Shortcuts" section in the doc list. This allows you to quickly access the doc from the "My Shortcuts" tab. Starring a doc does not affect the view for others in your workspace.`,
    expected: `Starred docs appear in the 'My Shortcuts' section of your doc list. When you star a doc, it is added to this section for easy access.`,
  },
}

export function ReviewModal({ open, onOpenChange }: ReviewModalProps) {
  const [selectedScores, setSelectedScores] = useState(
    reviewData.scores.reduce((acc, score) => ({ ...acc, [score.id]: score.checked }), {}),
  )
  const [currentScore, setCurrentScore] = useState(reviewData.currentScore)
  const [scoreValue, setScoreValue] = useState<string | null>(null)
  const [autoAdvance, setAutoAdvance] = useState(false)
  const [currentRow, setCurrentRow] = useState(reviewData.currentRow)

  const handleScoreSelect = (score: string) => {
    setScoreValue(score)
  }

  const handlePreviousRow = () => {
    if (currentRow > 1) {
      setCurrentRow(currentRow - 1)
    }
  }

  const handleNextRow = () => {
    if (currentRow < reviewData.totalRows) {
      setCurrentRow(currentRow + 1)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-7xl max-h-[95vh] p-0 overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold">Human review</h2>
            <span className="text-sm text-muted-foreground font-mono">{reviewData.id}</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-sm">
              <span>Row</span>
              <span className="font-medium">{currentRow}</span>
              <span className="text-muted-foreground">of {reviewData.totalRows}</span>
            </div>
            <Button variant="outline" size="sm" onClick={handlePreviousRow} disabled={currentRow === 1}>
              <ChevronLeft className="w-4 h-4 mr-1" />
              Previous row
            </Button>
            <Button variant="outline" size="sm" onClick={handleNextRow} disabled={currentRow === reviewData.totalRows}>
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
              {reviewData.scores.map((score) => (
                <div key={score.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={score.id}
                    checked={selectedScores[score.id as keyof typeof selectedScores]}
                    onCheckedChange={(checked) => setSelectedScores((prev) => ({ ...prev, [score.id]: checked }))}
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
              <div>
                <h2 className="text-xl font-semibold mb-4">response quality</h2>
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
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Scores</h4>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Factuality</span>
                      <span className="text-sm font-medium">avg_relevance</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">0.00%</span>
                      <span className="text-sm font-medium">80.00%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">max_relevance</span>
                      <span className="text-sm text-muted-foreground">min_relevance</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">80.00%</span>
                      <span className="text-sm font-medium">80.00%</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-muted-foreground">Factuality parsed</span>
                      <span></span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium">100.00%</span>
                      <span></span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Input */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Input</h4>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  <div className="mb-2">
                    <Badge variant="secondary">Markdown</Badge>
                    <ChevronDown className="w-4 h-4 ml-1 inline" />
                  </div>
                  <div className="text-sm">{reviewData.spanDetails.input}</div>
                </div>

                <Separator />

                {/* Output */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Output</h4>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  <div className="mb-2">
                    <Badge variant="secondary">Markdown</Badge>
                    <ChevronDown className="w-4 h-4 ml-1 inline" />
                  </div>
                  <div className="text-sm leading-relaxed">{reviewData.spanDetails.output}</div>
                </div>

                <Separator />

                {/* Expected */}
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
                    <div className="pl-4">{reviewData.spanDetails.expected}</div>
                  </div>
                </div>

                <Separator />

                {/* Metadata */}
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-medium">Metadata</h4>
                    <ChevronDown className="w-4 h-4" />
                  </div>
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

