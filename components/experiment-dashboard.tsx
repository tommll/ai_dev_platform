"use client"

import { useState } from "react"
import { ArrowLeft, ChevronDown, Filter, MoreHorizontal, Settings, Eye, Lock, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"

// Mock data based on the image
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

export function ExperimentDashboard() {
  const [selectedModels, setSelectedModels] = useState(["one", "two", "three", "four"])
  const [diffMode, setDiffMode] = useState(true)

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-black rounded-full" />
              <span className="text-sm text-muted-foreground">Acmecorp / Model comparison</span>
              <ChevronDown className="w-4 h-4 text-muted-foreground" />
            </div>
            <nav className="flex items-center gap-6">
              <Button variant="ghost" className="text-sm font-medium">
                Experiments
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground">
                Library
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground">
                Logs
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground">
                Playgrounds
              </Button>
              <Button variant="ghost" className="text-sm text-muted-foreground">
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

      {/* Experiment Header */}
      <div className="border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <h1 className="text-xl font-semibold">Experiment</h1>
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
            <Button variant="outline" size="sm">
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

      {/* Model Selection */}
      <div className="px-6 py-3 border-b">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="bg-gray-100">
              <div className="w-2 h-2 bg-gray-500 rounded-full mr-2" />
              one
            </Badge>
            <span className="text-sm text-muted-foreground">compared with</span>
            <Badge variant="outline" className="bg-purple-50">
              <div className="w-2 h-2 bg-purple-500 rounded-full mr-2" />
              two
            </Badge>
            <Badge variant="outline" className="bg-blue-50">
              <div className="w-2 h-2 bg-blue-500 rounded-full mr-2" />
              three
            </Badge>
            <Badge variant="outline" className="bg-orange-50">
              <div className="w-2 h-2 bg-orange-500 rounded-full mr-2" />
              four
            </Badge>
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

          {/* Score Distribution Chart */}
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="text-sm font-medium">Score distribution for ExactMatch</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-1 h-20 mb-4">
                <div className="bg-gray-500 w-8 h-16 rounded-sm" />
                <div className="bg-purple-500 w-8 h-12 rounded-sm" />
                <div className="bg-blue-500 w-8 h-4 rounded-sm" />
                <div className="bg-orange-500 w-8 h-8 rounded-sm" />
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>0%</span>
                <span>10%</span>
                <span>20%</span>
                <span>30%</span>
                <span>40%</span>
                <span>50%</span>
                <span>60%</span>
                <span>70%</span>
                <span>80%</span>
                <span>90%</span>
                <span>100%</span>
              </div>
            </CardContent>
          </Card>

          {/* Results Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Input</TableHead>
                  <TableHead>Output</TableHead>
                  <TableHead>Expected</TableHead>
                  <TableHead>ExactMatch</TableHead>
                  <TableHead>Levenstein</TableHead>
                  <TableHead>Duration</TableHead>
                  <TableHead>LLM</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {experimentData.map((row, index) => (
                  <TableRow key={row.id}>
                    <TableCell>
                      <div className="w-4 h-4 bg-blue-500 rounded-sm flex items-center justify-center">
                        <span className="text-xs text-white">eval</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium">eval</TableCell>
                    <TableCell className="max-w-xs">
                      <div className="truncate">{row.input}</div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {row.outputs.map((output, i) => (
                          <div key={i} className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${output.color}`} />
                            <span className="text-sm truncate max-w-xs">{output.value}</span>
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>{row.expected}</TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {row.outputs.map((_, i) => (
                          <div key={i} className="text-sm">
                            {i === 0
                              ? row.exactMatch
                              : i < row.levenstein.length
                                ? row.exactMatch === "100.0%"
                                  ? "100.0%"
                                  : "0.0%"
                                : ""}
                            {row.exactMatch === "100.0%" && i > 0 && i < row.outputs.length && (
                              <span className="text-green-600 ml-1">+100.0%</span>
                            )}
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {row.levenstein.map((score, i) => (
                          <div key={i} className="text-sm">
                            {score}
                            {i === 1 && row.id === "eval-1" && <span className="text-red-500 ml-1">-40.0%</span>}
                            {i === 2 && row.id === "eval-1" && <span className="text-green-600 ml-1">+18.2%</span>}
                            {i === 1 && row.id === "eval-2" && <span className="text-green-600 ml-1">+18.1%</span>}
                            {i === 1 && row.id === "eval-3" && <span className="text-green-600 ml-1">+100.0%</span>}
                            {i === 2 && row.id === "eval-3" && <span className="text-green-600 ml-1">+99.3%</span>}
                            {i === 3 && row.id === "eval-3" && <span className="text-green-600 ml-1">+80.0%</span>}
                            {i === 1 && row.id === "eval-4" && <span className="text-green-600 ml-1">+100.0%</span>}
                            {i === 0 && row.id === "eval-4" && <span className="text-green-600 ml-1">+20.0%</span>}
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {row.duration.map((duration, i) => (
                          <div key={i} className="text-sm">
                            {duration}
                          </div>
                        ))}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        {row.llm.map((llm, i) => (
                          <div key={i} className="text-sm">
                            {llm}
                          </div>
                        ))}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Scores Sidebar */}
        <div className="w-80 border-l bg-muted/20 p-6">
          <h2 className="font-semibold mb-4 flex items-center justify-between">
            Scores
            <Button variant="ghost" size="icon">
              <Settings className="w-4 h-4" />
            </Button>
          </h2>

          <div className="space-y-6">
            {/* Levenstein */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Levenstein</span>
                <span className="text-xs text-muted-foreground">5</span>
              </div>
              <div className="text-2xl font-bold">68.00%</div>
              <div className="space-y-2 mt-3">
                {scoreMetrics.levenstein.distribution.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded ${item.color}`} />
                      <Progress value={item.value} className="w-16 h-2" />
                    </div>
                    <div className="text-sm">
                      <span className="text-green-600">{item.change}</span>
                      <span className="text-muted-foreground ml-2">+1</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* ExactMatch */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">ExactMatch</span>
                <span className="text-xs text-muted-foreground">5</span>
              </div>
              <div className="text-2xl font-bold">60.00%</div>
              <div className="space-y-2 mt-3">
                {scoreMetrics.exactMatch.distribution.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded ${item.color}`} />
                      <span className="text-sm">{item.value.toFixed(2)}%</span>
                    </div>
                    <div className="text-sm">
                      <span className="text-green-600">{item.change}</span>
                      <span className="text-muted-foreground ml-2">+{i === 2 ? 1 : 3}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Duration */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Avg Duration</span>
                <span className="text-xs text-muted-foreground">5</span>
              </div>
              <div className="text-2xl font-bold text-blue-600">59.17s</div>
              <div className="space-y-2 mt-3">
                {scoreMetrics.duration.avgValues.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm">{item.value}</span>
                    <div className="text-sm">
                      <span className="text-green-600">{item.change}</span>
                      <span className="text-muted-foreground ml-2">+5</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* LLM Duration */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Avg LLM duration</span>
                <span className="text-xs text-muted-foreground">5</span>
              </div>
              <div className="text-2xl font-bold">0.1668s</div>
              <div className="space-y-2 mt-3">
                {scoreMetrics.llmDuration.avgValues.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm">{item.value}</span>
                    <div className="text-sm">
                      <span className={i === 0 ? "text-green-600" : "text-red-500"}>{item.change}</span>
                      <span className="text-muted-foreground ml-2">+{i === 0 ? 4 : 3}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
