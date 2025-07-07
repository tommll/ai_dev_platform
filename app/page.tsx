"use client"

import { useState } from "react"
import { useAuth } from "@/hooks/useAuth"
import { LoginForm } from "@/components/login-form"
import { ExperimentDashboard } from "@/components/experiment-dashboard"
import { ExperimentsList } from "@/components/experiments-list"
import { PromptsList } from "@/components/prompts-list"
import { DatasetsList } from "@/components/datasets-list"
import { Loader2 } from "lucide-react"

export default function Page() {
  const { isAuthenticated, isLoading } = useAuth()
  const [currentTab, setCurrentTab] = useState("experiments")
  const [showReviewModal, setShowReviewModal] = useState(false)
  const [currentProjectId] = useState(1) // Default project ID

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading...</span>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return <LoginForm />
  }

  const handleTabChange = (tab: string) => {
    setCurrentTab(tab)
  }

  const handleShowReview = () => {
    setShowReviewModal(true)
  }

  const renderContent = () => {
    switch (currentTab) {
      case "experiments":
        return <ExperimentsList projectId={currentProjectId} />
      case "prompts":
        return <PromptsList projectId={currentProjectId} />
      case "datasets":
        return <DatasetsList projectId={currentProjectId} />
      case "dashboard":
        return <ExperimentDashboard onTabChange={handleTabChange} onShowReview={handleShowReview} />
      default:
        return <ExperimentsList projectId={currentProjectId} />
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
                LLM Development Platform
              </span>
            </div>
            <nav className="flex items-center gap-6">
              <button
                onClick={() => handleTabChange("experiments")}
                className={`text-sm font-medium transition-colors ${currentTab === "experiments"
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                Experiments
              </button>
              <button
                onClick={() => handleTabChange("prompts")}
                className={`text-sm font-medium transition-colors ${currentTab === "prompts"
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                Prompts
              </button>
              <button
                onClick={() => handleTabChange("datasets")}
                className={`text-sm font-medium transition-colors ${currentTab === "datasets"
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                Datasets
              </button>
              <button
                onClick={() => handleTabChange("dashboard")}
                className={`text-sm font-medium transition-colors ${currentTab === "dashboard"
                  ? "text-foreground"
                  : "text-muted-foreground hover:text-foreground"
                  }`}
              >
                Dashboard
              </button>
            </nav>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Project ID: {currentProjectId}
            </span>
          </div>
        </div>
      </header>

      {/* Content */}
      <main>
        {renderContent()}
      </main>
    </div>
  )
}