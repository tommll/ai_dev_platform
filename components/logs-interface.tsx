"use client"

import { useState } from "react"
import {
  ChevronDown,
  Settings,
  Filter,
  MoreHorizontal,
  Plus,
  Copy,
  Search,
  ArrowUp,
  ArrowDown,
  Link,
  Triangle,
  RefreshCw,
  Database,
  Zap,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { ScrollArea } from "@/components/ui/scroll-area"

interface LogsInterfaceProps {
  onTabChange: (tab: string) => void
}

const logsData = [
  {
    id: "1",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "25.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "2",
    name: "run_full_chat",
    input: '{"query":"Ca..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "100.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "3",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"get","path":...}',
    no_hallucination: "100.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "4",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "100.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "5",
    name: "run_full_chat",
    input: '{"query":"Su..."}',
    output: '{"op":"patch","path"...}',
    no_hallucination: "25.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "6",
    name: "run_full_chat",
    input: '{"query":"ho..."}',
    output: '{"op":"get","path":...}',
    no_hallucination: "100.00%",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "7",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "8",
    name: "run_full_chat",
    input: '{"query":"Ca..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "9",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"get","path":...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "10",
    name: "run_full_chat",
    input: '{"query":"Ho..."}',
    output: '{"op":"post","path"...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "11",
    name: "run_full_chat",
    input: '{"query":"Su..."}',
    output: '{"op":"patch","path"...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
  {
    id: "12",
    name: "run_full_chat",
    input: '{"query":"ho..."}',
    output: '{"op":"get","path":...}',
    no_hallucination: "–",
    traceId: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  },
]

const traceData = {
  id: "870bcd48-fb40-44c1-b413-a3e9104ee0b7",
  spans: [
    {
      id: "run_full_chat",
      name: "run_full_chat",
      duration: "0.83s",
      type: "root",
      expanded: true,
      children: [
        {
          id: "perform_chat_st",
          name: "perform_chat_st...",
          duration: "0.83s",
          type: "span",
          expanded: true,
          children: [
            {
              id: "chat_c",
              name: "Chat C...",
              duration: "0.27s",
              tokens: "253 tok",
              type: "llm",
            },
          ],
        },
        {
          id: "search",
          name: "search",
          duration: "0.25s",
          type: "span",
          expanded: false,
        },
        {
          id: "embed",
          name: "Embed...",
          duration: "0.24s",
          tokens: "2 tok",
          type: "embedding",
        },
        {
          id: "chat_main",
          name: "Chat ...",
          duration: "0.30s",
          tokens: "3054 tok",
          type: "llm",
        },
        {
          id: "run_hallucination",
          name: "run_hallucinati...",
          duration: "0.49s",
          type: "span",
          expanded: true,
          children: [
            {
              id: "cha",
              name: "Cha...",
              duration: "0.48s",
              tokens: "1266 tok",
              type: "llm",
            },
          ],
        },
      ],
    },
  ],
}

const spanDetails = {
  embedding: {
    type: "Embedding",
    start: "Aug 12 7:31 PM",
    offset: "0.28s",
    duration: "0.24s",
    totalTokens: "2",
    promptTokens: "2",
    cached: "true",
    input: "create evaluation",
    output: "embedding_length: 1536",
    expected: "null",
  },
}

export function LogsInterface({ onTabChange }: LogsInterfaceProps) {
  const [selectedTrace, setSelectedTrace] = useState(traceData)
  const [selectedSpan, setSelectedSpan] = useState("embed")
  const [inputFormat, setInputFormat] = useState("markdown")
  const [outputFormat, setOutputFormat] = useState("yaml")
  const [expectedFormat, setExpectedFormat] = useState("yaml")
  const [metadataFormat, setMetadataFormat] = useState("yaml")

  const getSpanIcon = (type: string) => {
    switch (type) {
      case "llm":
        return (
          <div className="w-4 h-4 bg-purple-500 rounded-sm flex items-center justify-center">
            <span className="text-xs text-white font-bold">C</span>
          </div>
        )
      case "embedding":
        return (
          <div className="w-4 h-4 bg-purple-500 rounded-sm flex items-center justify-center">
            <span className="text-xs text-white font-bold">E</span>
          </div>
        )
      case "span":
        return (
          <div className="w-4 h-4 bg-blue-500 rounded-sm flex items-center justify-center">
            <span className="text-xs text-white font-bold">i</span>
          </div>
        )
      default:
        return (
          <div className="w-4 h-4 bg-blue-500 rounded-sm flex items-center justify-center">
            <span className="text-xs text-white font-bold">i</span>
          </div>
        )
    }
  }

  const renderSpanTree = (spans: any[], level = 0) => {
    return spans.map((span) => (
      <div key={span.id}>
        <div
          className={`flex items-center gap-2 p-2 rounded cursor-pointer hover:bg-muted/50 ${selectedSpan === span.id ? "bg-blue-50 border-l-2 border-blue-500" : ""
            }`}
          style={{ marginLeft: `${level * 24}px` }}
          onClick={() => setSelectedSpan(span.id)}
        >
          {span.children && <Triangle className={`w-3 h-3 fill-current ${span.expanded ? "rotate-90" : ""}`} />}
          {getSpanIcon(span.type)}
          <span className="text-sm font-medium">{span.name}</span>
          <div className="ml-auto flex items-center gap-2 text-xs text-muted-foreground">
            {span.tokens && <span>{span.tokens}</span>}
            <span>{span.duration}</span>
          </div>
        </div>
        {span.children && span.expanded && renderSpanTree(span.children, level + 1)}
      </div>
    ))
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-black rounded-full" />
              <span className="text-sm text-muted-foreground">Acmecorp / APIagent</span>
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
              <Button variant="ghost" className="text-sm font-medium">
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
            <div className="w-8 h-8 bg-muted rounded-full" />
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Left Panel - Logs Table */}
        <div className="w-1/2 p-6 border-r">
          <div className="flex items-center justify-between mb-6">
            <h1 className="text-2xl font-semibold">Logs</h1>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Settings className="w-4 h-4 mr-2" />
                Review
              </Button>
              <Button variant="ghost" size="icon">
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-4 mb-6">
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

          {/* Logs Table */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12"></TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Input</TableHead>
                  <TableHead>Output</TableHead>
                  <TableHead>no_hallucination</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logsData.map((row) => (
                  <TableRow
                    key={row.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => setSelectedTrace(traceData)}
                  >
                    <TableCell>
                      <div className="w-4 h-4 bg-blue-500 rounded-sm flex items-center justify-center">
                        <span className="text-xs text-white font-mono">i</span>
                      </div>
                    </TableCell>
                    <TableCell className="font-medium text-blue-600">{row.name}</TableCell>
                    <TableCell className="font-mono text-sm max-w-xs truncate">{row.input}</TableCell>
                    <TableCell className="font-mono text-sm max-w-xs truncate">{row.output}</TableCell>
                    <TableCell>
                      {row.no_hallucination !== "–" ? (
                        <span className={row.no_hallucination === "100.00%" ? "text-green-600" : "text-orange-600"}>
                          {row.no_hallucination}
                        </span>
                      ) : (
                        <span className="text-muted-foreground">–</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </div>

        {/* Right Panel - Trace Details */}
        <div className="flex-1 bg-muted/20">
          {/* Trace Header */}
          <div className="border-b p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon">
                  <Copy className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <ArrowUp className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <ArrowDown className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="ghost" size="icon">
                  <Link className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Search className="w-4 h-4" />
                </Button>
                <Button variant="ghost" size="icon">
                  <MoreHorizontal className="w-4 h-4" />
                </Button>
              </div>
            </div>
            <div className="text-xs text-muted-foreground font-mono">{selectedTrace.id}</div>
          </div>

          <div className="flex h-full">
            {/* Trace Tree */}
            <div className="w-1/2 border-r">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium">Trace</h3>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon">
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Plus className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <Copy className="w-4 h-4" />
                    </Button>
                  </div>
                </div>

                <ScrollArea className="h-[400px]">{renderSpanTree(selectedTrace.spans)}</ScrollArea>
              </div>
            </div>

            {/* Span Details */}
            <div className="flex-1">
              <div className="p-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-medium">Span</h3>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon">
                      <Plus className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm">
                      <Database className="w-4 h-4 mr-2" />
                      Add to dataset
                    </Button>
                    <Button variant="outline" size="sm">
                      <Zap className="w-4 h-4 mr-2" />
                      Try prompt
                    </Button>
                  </div>
                </div>

                <ScrollArea className="h-[600px]">
                  {/* Span Info */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <div className="w-6 h-6 bg-purple-500 rounded flex items-center justify-center">
                        <span className="text-sm text-white font-bold">E</span>
                      </div>
                      <span className="font-medium">Embedding</span>
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Start</div>
                        <div>Aug 12 7:31 PM</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Offset</div>
                        <div>0.28s</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Duration</div>
                        <div>0.24s</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Total tokens</div>
                        <div>2</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Prompt tokens</div>
                        <div>2</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Cached</div>
                        <div>true</div>
                      </div>
                    </div>

                    <Separator />

                    {/* Input Section */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">Input</h4>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Select value={inputFormat} onValueChange={setInputFormat}>
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="markdown">Markdown</SelectItem>
                            <SelectItem value="yaml">YAML</SelectItem>
                            <SelectItem value="json">JSON</SelectItem>
                          </SelectContent>
                        </Select>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="bg-muted p-3 rounded text-sm">create evaluation</div>
                    </div>

                    {/* Output Section */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">Output</h4>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Select value={outputFormat} onValueChange={setOutputFormat}>
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="yaml">YAML</SelectItem>
                            <SelectItem value="markdown">Markdown</SelectItem>
                            <SelectItem value="json">JSON</SelectItem>
                          </SelectContent>
                        </Select>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="bg-muted p-3 rounded text-sm font-mono">
                        <div className="text-blue-600">1</div>
                        <div className="ml-4">
                          <span className="text-purple-600">embedding_length:</span> 1536
                        </div>
                      </div>
                    </div>

                    {/* Expected Section */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">Expected</h4>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Select value={expectedFormat} onValueChange={setExpectedFormat}>
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="yaml">YAML</SelectItem>
                            <SelectItem value="markdown">Markdown</SelectItem>
                            <SelectItem value="json">JSON</SelectItem>
                          </SelectContent>
                        </Select>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                      <div className="bg-muted p-3 rounded text-sm font-mono">
                        <div className="text-blue-600">1</div>
                        <div className="ml-4 text-muted-foreground">null</div>
                      </div>
                    </div>

                    {/* Metadata Section */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium">Metadata</h4>
                        <div className="flex items-center gap-2">
                          <ChevronDown className="w-4 h-4" />
                          <Button variant="ghost" size="icon">
                            <Settings className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Select value={metadataFormat} onValueChange={setMetadataFormat}>
                          <SelectTrigger className="w-32">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="yaml">YAML</SelectItem>
                            <SelectItem value="markdown">Markdown</SelectItem>
                            <SelectItem value="json">JSON</SelectItem>
                          </SelectContent>
                        </Select>
                        <ChevronDown className="w-4 h-4" />
                      </div>
                    </div>
                  </div>
                </ScrollArea>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
