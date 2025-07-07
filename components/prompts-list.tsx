"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Edit, Trash2, Copy, Eye, Settings } from "lucide-react"
import { usePrompts } from "@/hooks/usePrompts"
import { usePromptVersions } from "@/hooks/usePrompts"

interface PromptsListProps {
    projectId: number
}

export function PromptsList({ projectId }: PromptsListProps) {
    const { prompts, isLoading, error, createPrompt } = usePrompts(projectId)
    const [selectedPromptId, setSelectedPromptId] = useState<number | null>(null)

    // Get versions for the selected prompt
    const { versions, createVersion, deployVersion } = usePromptVersions(selectedPromptId || 0)

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
                            <p>Error loading prompts: {error}</p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    if (prompts.length === 0) {
        return (
            <div className="p-6">
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center text-gray-500">
                            <p>No prompts found. Create your first prompt to get started.</p>
                            <Button className="mt-4">Create Prompt</Button>
                        </div>
                    </CardContent>
                </Card>
            </div>
        )
    }

    return (
        <div className="p-6 space-y-4">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold">Prompts</h2>
                <Button>Create New Prompt</Button>
            </div>

            <div className="grid gap-4">
                {prompts.map((prompt) => (
                    <Card key={prompt.id} className="hover:shadow-md transition-shadow">
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <div>
                                    <CardTitle className="text-lg">{prompt.name}</CardTitle>
                                    <p className="text-sm text-muted-foreground mt-1">
                                        {prompt.description || "No description"}
                                    </p>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Badge
                                        variant={prompt.is_deployed ? "default" : "outline"}
                                        className={prompt.is_deployed ? "bg-green-500" : ""}
                                    >
                                        {prompt.is_deployed ? "Deployed" : "Draft"}
                                    </Badge>
                                    <div className="flex items-center gap-1">
                                        <Button variant="ghost" size="sm">
                                            <Eye className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Edit className="w-4 h-4" />
                                        </Button>
                                        <Button variant="ghost" size="sm">
                                            <Copy className="w-4 h-4" />
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
                                        {prompt.is_active ? "Active" : "Inactive"}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-muted-foreground">Created:</span>
                                    <span className="ml-2 font-medium">
                                        {new Date(prompt.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="mt-4 flex items-center gap-2">
                                <Button size="sm">
                                    <Settings className="w-4 h-4 mr-2" />
                                    Manage Versions
                                </Button>
                                <Button variant="outline" size="sm">
                                    <Edit className="w-4 h-4 mr-2" />
                                    Edit
                                </Button>
                                {!prompt.is_deployed && (
                                    <Button variant="outline" size="sm">
                                        Deploy
                                    </Button>
                                )}
                            </div>

                            {/* Show recent versions if any */}
                            {versions.length > 0 && (
                                <div className="mt-4">
                                    <h4 className="text-sm font-medium mb-2">Recent Versions</h4>
                                    <div className="space-y-2">
                                        {versions.slice(0, 3).map((version) => (
                                            <div key={version.id} className="flex items-center justify-between text-sm">
                                                <div className="flex items-center gap-2">
                                                    <div className={`w-2 h-2 rounded-full ${version.is_deployed ? 'bg-green-500' : 'bg-gray-500'
                                                        }`} />
                                                    <span>v{version.version}</span>
                                                    {version.is_deployed && (
                                                        <Badge variant="outline" className="text-xs">Deployed</Badge>
                                                    )}
                                                </div>
                                                <div className="flex items-center gap-2">
                                                    <span className="text-muted-foreground">
                                                        {new Date(version.created_at).toLocaleDateString()}
                                                    </span>
                                                    {!version.is_deployed && (
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={() => deployVersion(version.version)}
                                                        >
                                                            Deploy
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