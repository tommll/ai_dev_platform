"use client"

import { useState } from "react"
import { LogsInterface } from "@/components/logs-interface"
import { PlaygroundInterface } from "@/components/playground-interface"
import { ExperimentDashboard } from "@/components/experiment-dashboard"
import { ReviewModal } from "@/components/review-modal"

export default function Page() {
  const [activeTab, setActiveTab] = useState("experiments")
  const [showReviewModal, setShowReviewModal] = useState(false)

  const renderContent = () => {
    switch (activeTab) {
      case "logs":
        return <LogsInterface onTabChange={setActiveTab} />
      case "playgrounds":
        return <PlaygroundInterface onTabChange={setActiveTab} />
      case "experiments":
      default:
        return <ExperimentDashboard onTabChange={setActiveTab} onShowReview={() => setShowReviewModal(true)} />
    }
  }

  return (
    <>
      {renderContent()}
      <ReviewModal open={showReviewModal} onOpenChange={setShowReviewModal} />
    </>
  )
}
