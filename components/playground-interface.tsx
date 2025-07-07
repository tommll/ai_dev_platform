"use client"

import { useState } from "react"
import { ChevronDown, Settings, ArrowLeft, Lock, Plus, Play, MoreHorizontal, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { ScrollArea } from "@/components/ui/scroll-area"

interface PlaygroundInterfaceProps {
  onTabChange: (tab: string) => void
}

const promptConfigs = [
  {
    id: "A",
    label: "Prompt",
    model: "GPT 4o",
    color: "bg-blue-50 border-blue-200",
    borderColor: "border-l-blue-500",
    textColor: "text-blue-600",
    systemPrompt: "What is the most noteworthy part of this article?",
    userInput: "{{input}}",
  },
  {
    id: "B",
    label: "Prompt",
    model: "LLaMA 3.1 8B Instruct Turbo",
    color: "bg-pink-50 border-pink-200",
    borderColor: "border-l-pink-500",
    textColor: "text-pink-600",
    systemPrompt: "What is the most noteworthy part of this article?",
    userInput: "{{input}}",
  },
  {
    id: "C",
    label: "Prompt",
    model: "GPT 4o",
    color: "bg-green-50 border-green-200",
    borderColor: "border-l-green-500",
    textColor: "text-green-600",
    systemPrompt: "What is the most noteworthy sentence in this article?",
    userInput: "{{input}}",
  },
  {
    id: "D",
    label: "Prompt",
    model: "GPT 4o",
    color: "bg-purple-50 border-purple-200",
    borderColor: "border-l-purple-500",
    textColor: "text-purple-600",
    systemPrompt: "What is the most noteworthy article? Print that and nothing",
    userInput: "{{input}}",
  },
]

const datasetRows = [
  {
    id: 1,
    input: `TORONTO, Sept. 3, 2024 - Katherine Gibson, Interim Chief Financial Officer of Royal Bank of Canada (TSX: RY) (NYSE: RY), is scheduled to speak at the Barclays Global Financial Services Conference in New York on`,
    outputs: {
      A: {
        text: "The most noteworthy part of the article is that Katherine Gibson, the Interim Chief Financial Officer of Royal Bank of Canada (RBC), is scheduled to speak at the Barclays Global Financial Services Conference in New York",
        duration: "1.23s",
        summary: "Summary 100.00%",
      },
      B: {
        text: "The most noteworthy part of this article is that Katherine Gibson, Interim Chief Financial Officer of Royal Bank of Canada, will be speaking at the Barclays Global Financial Services in New York on",
        duration: "0.27s",
        summary: "Summary 100.00%",
      },
      C: {
        text: "Summary 100.00%",
        duration: "1.49s",
        summary: "Summary 100.00%",
      },
      D: {
        text: `"Katherine Gibson, Interim Chief Financial Officer of Royal Bank of Canada (TSX: RY) (NYSE: RY), is scheduled to speak at the Barclays Global Financial Services Conference in New York on"`,
        duration: "1.13s",
        summary: "Summary 100.00%",
      },
    },
  },
]

export function PlaygroundInterface({ onTabChange }: PlaygroundInterfaceProps) {
  const [selectedPrompts, setSelectedPrompts] = useState(["A", "B", "C", "D"])

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-black rounded-full" />
              <span className="text-sm text-muted-foreground">Acmecorp / Financial press</span>
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            </div>
            <nav className="flex items-center gap-6">
              <Button
                variant="ghost"
                className="text-sm text-muted-foreground"
                onClick={() => onTabChange("experiments")}
              >
                Experiments
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground" onClick={() => onTabChange("library")}>
                Library
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground" onClick={() => onTabChange("logs")}>
                Logs
              </Button>
              <Button variant="ghost" className="text-sm font-medium">
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
            <div className="w-8 h-8 bg-muted rounded-full" />
          </div>
        </div>
      </header>

      {/* Playground Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <h1 className="text-xl font-semibold">Summarize</h1>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm">
              <Lock className="w-4 h-4 mr-2" />
              Private
            </Button>
            <Button variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Prompt
            </Button>
            <Button variant="ghost" size="icon">
              <MoreHorizontal className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Prompt Configuration Grid */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          {promptConfigs.map((config) => (
            <Card key={config.id} className={`${config.color} min-h-[400px]`}>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div
                      className={`w-6 h-6 rounded flex items-center justify-center text-sm font-bold ${config.id === "A"
                          ? "bg-blue-600 text-white"
                          : config.id === "B"
                            ? "bg-pink-600 text-white"
                            : config.id === "C"
                              ? "bg-green-600 text-white"
                              : "bg-purple-600 text-white"
                        }`}
                    >
                      {config.id}
                    </div>
                    <span className="font-medium">{config.label}</span>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Model Selection */}
                <div className="flex items-center gap-2">
                  <div className="w-6 h-6 bg-gray-800 rounded flex items-center justify-center">
                    {config.model.includes("LLaMA") ? (
                      <div className="w-4 h-4 bg-blue-500 rounded-full" />
                    ) : (
                      <Settings className="w-3 h-3 text-white" />
                    )}
                  </div>
                  <Select defaultValue={config.model.toLowerCase().replace(/\s+/g, "-")}>
                    <SelectTrigger className="flex-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="gpt-4o">GPT 4o</SelectItem>
                      <SelectItem value="llama-3.1-8b-instruct-turbo">LLaMA 3.1 8B Instruct Turbo</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button variant="ghost" size="icon">
                    <Settings className="w-4 h-4" />
                  </Button>
                </div>

                {/* System Prompt */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium">System</span>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  <Textarea
                    value={config.systemPrompt}
                    className="min-h-[80px] text-sm resize-none"
                    placeholder="Enter system prompt..."
                  />
                </div>

                {/* User Input */}
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-sm font-medium">User</span>
                    <ChevronDown className="w-4 h-4" />
                  </div>
                  <div className="bg-muted p-3 rounded text-sm font-mono text-purple-600 border">
                    {config.userInput}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex items-center gap-2 pt-4">
                  <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                    <Plus className="w-4 h-4 mr-2" />
                    Message
                  </Button>
                  <Button variant="outline" size="sm">
                    <Settings className="w-4 h-4 mr-2" />
                    Tools
                    <ChevronDown className="w-4 h-4 ml-1" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Dataset and Controls */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium">12 dataset rows</span>
            <Button variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Row
            </Button>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
            <Badge variant="outline" className="bg-purple-50">
              <Settings className="w-4 h-4 mr-2" />
              Press releases
              <ChevronDown className="w-4 h-4 ml-2" />
            </Badge>
            <Button variant="ghost" size="icon">
              <X className="w-4 h-4" />
            </Button>
            <Badge variant="outline" className="bg-green-50">
              <span className="text-green-600">✓</span>
              <span className="ml-1">1 scorer</span>
              <ChevronDown className="w-4 h-4 ml-2" />
            </Badge>
            <Button variant="outline" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Experiments
            </Button>
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Play className="w-4 h-4 mr-2" />
              Run
            </Button>
          </div>
        </div>

        {/* Results Table */}
        <div className="border rounded-lg overflow-hidden">
          <ScrollArea className="w-full">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">Input</TableHead>
                  <TableHead className="text-blue-600 min-w-[300px]">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">A</span>
                      <span>Output</span>
                    </div>
                    <div className="text-xs text-muted-foreground font-normal">AVG Summary 100.00%</div>
                  </TableHead>
                  <TableHead className="text-pink-600 min-w-[300px]">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">B</span>
                      <span>Output</span>
                    </div>
                    <div className="text-xs text-muted-foreground font-normal">AVG Summary 100.00%</div>
                  </TableHead>
                  <TableHead className="text-green-600 min-w-[300px]">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">C</span>
                      <span>Output</span>
                    </div>
                    <div className="text-xs text-muted-foreground font-normal">AVG Summary 100.00%</div>
                  </TableHead>
                  <TableHead className="text-purple-600 min-w-[300px]">
                    <div className="flex items-center gap-2">
                      <span className="font-bold">D</span>
                      <span>Output</span>
                    </div>
                  </TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {datasetRows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell className="font-bold text-center align-top pt-4">{row.id}</TableCell>
                    <TableCell className="align-top border-l-2 border-l-blue-500">
                      <div className="space-y-2">
                        <div className="text-sm leading-relaxed">{row.outputs.A.text}</div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{row.outputs.A.summary}</span>
                          <span>{row.outputs.A.duration}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top border-l-2 border-l-pink-500">
                      <div className="space-y-2">
                        <div className="text-sm leading-relaxed">{row.outputs.B.text}</div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{row.outputs.B.summary}</span>
                          <span>{row.outputs.B.duration}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top border-l-2 border-l-green-500">
                      <div className="space-y-2">
                        <div className="text-sm leading-relaxed">{row.outputs.C.text}</div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{row.outputs.C.summary}</span>
                          <span>{row.outputs.C.duration}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell className="align-top border-l-2 border-l-purple-500">
                      <div className="space-y-2">
                        <div className="text-sm leading-relaxed">
                          <div className="bg-blue-50 p-2 rounded font-mono text-xs mb-2">
                            <span className="text-blue-600">JSON</span>
                          </div>
                          {row.outputs.D.text}
                        </div>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>{row.outputs.D.summary}</span>
                          <span>{row.outputs.D.duration}</span>
                        </div>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </ScrollArea>
        </div>

        {/* Input Data Display */}
        <div className="mt-6 p-4 bg-muted/30 rounded-lg">
          <div className="text-sm text-muted-foreground mb-2">Input Data:</div>
          <div className="text-sm font-mono bg-muted p-3 rounded">{datasetRows[0].input}</div>
        </div>
      </div>
    </div>
  )
}
