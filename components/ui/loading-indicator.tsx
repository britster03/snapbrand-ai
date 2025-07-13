"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Badge } from "@/components/ui/badge"
import { 
  Sparkles, 
  Brain, 
  Palette, 
  Zap, 
  CheckCircle, 
  Loader2,
  Image as ImageIcon,
  Wand2,
  Stars,
  Cpu,
  CloudUpload
} from "lucide-react"

interface LoadingIndicatorProps {
  isLoading: boolean
  numImages: number
  prompt: string
  onComplete?: () => void
}

interface LoadingStage {
  id: string
  title: string
  description: string
  icon: React.ElementType
  duration: number
  color: string
}

const loadingStages: LoadingStage[] = [
  {
    id: "analyzing",
    title: "Analyzing Prompt",
    description: "Understanding your creative vision",
    icon: Brain,
    duration: 2000,
    color: "text-blue-600"
  },
  {
    id: "processing",
    title: "Processing AI Model",
    description: "Engaging Amazon Titan V2 neural networks",
    icon: Cpu,
    duration: 3000,
    color: "text-purple-600"
  },
  {
    id: "generating",
    title: "Generating Images",
    description: "Creating your professional visuals",
    icon: Wand2,
    duration: 4000,
    color: "text-emerald-600"
  },
  {
    id: "enhancing",
    title: "Quality Enhancement",
    description: "Applying professional quality controls",
    icon: Stars,
    duration: 2000,
    color: "text-orange-600"
  },
  {
    id: "uploading",
    title: "Uploading to Cloud",
    description: "Storing your images securely",
    icon: CloudUpload,
    duration: 1500,
    color: "text-indigo-600"
  }
]

export function LoadingIndicator({ isLoading, numImages, prompt, onComplete }: LoadingIndicatorProps) {
  const [currentStage, setCurrentStage] = useState(0)
  const [progress, setProgress] = useState(0)
  const [stageProgress, setStageProgress] = useState(0)
  const [completedStages, setCompletedStages] = useState<Set<number>>(new Set())

  useEffect(() => {
    if (!isLoading) {
      // Reset state when not loading
      setCurrentStage(0)
      setProgress(0)
      setStageProgress(0)
      setCompletedStages(new Set())
      return
    }

    let stageIndex = 0
    let totalElapsed = 0

    const advanceStage = () => {
      if (stageIndex >= loadingStages.length) {
        setProgress(100)
        setTimeout(() => {
          onComplete?.()
        }, 500)
        return
      }

      const stage = loadingStages[stageIndex]
      const stageStart = Date.now()
      
      setCurrentStage(stageIndex)
      setStageProgress(0)

      const stageInterval = setInterval(() => {
        const elapsed = Date.now() - stageStart
        const stageProgressPercent = Math.min((elapsed / stage.duration) * 100, 100)
        setStageProgress(stageProgressPercent)

        // Update overall progress
        const overallProgress = ((stageIndex + (stageProgressPercent / 100)) / loadingStages.length) * 100
        setProgress(overallProgress)

        if (elapsed >= stage.duration) {
          clearInterval(stageInterval)
          setCompletedStages(prev => new Set(prev).add(stageIndex))
          stageIndex++
          totalElapsed += elapsed
          
          // Small delay between stages for visual appeal
          setTimeout(advanceStage, 300)
        }
      }, 50)
    }

    advanceStage()
  }, [isLoading, onComplete])

  if (!isLoading) return null

  const currentStageData = loadingStages[currentStage]

  return (
    <Card className="border-2 border-dashed border-blue-200 bg-gradient-to-br from-blue-50 via-purple-50 to-indigo-50">
      <CardContent className="p-8">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center space-y-2">
            <div className="flex items-center justify-center space-x-2">
              <div className="relative">
                <Sparkles className="w-8 h-8 text-blue-600 animate-pulse" />
                <div className="absolute inset-0 animate-ping">
                  <Sparkles className="w-8 h-8 text-blue-400 opacity-75" />
                </div>
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Creating Magic
              </h3>
            </div>
            <p className="text-sm text-gray-600">
              Generating {numImages} professional image{numImages > 1 ? 's' : ''} with AI
            </p>
          </div>

          {/* Prompt Preview */}
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-4 border border-blue-200">
            <div className="flex items-start space-x-3">
              <ImageIcon className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
              <div className="flex-1">
                <p className="text-sm font-medium text-gray-800 mb-1">Your Vision:</p>
                <p className="text-sm text-gray-600 line-clamp-2">{prompt}</p>
              </div>
            </div>
          </div>

          {/* Current Stage */}
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <div className="relative">
                <div className={`w-12 h-12 rounded-full bg-gradient-to-br from-white to-gray-100 border-2 border-blue-200 flex items-center justify-center ${currentStageData?.color}`}>
                  {currentStageData && (
                    <currentStageData.icon className="w-6 h-6 animate-pulse" />
                  )}
                </div>
                <div className="absolute inset-0 rounded-full border-2 border-blue-400 animate-pulse opacity-50"></div>
              </div>
              <div className="flex-1">
                <div className="flex items-center space-x-2">
                  <h4 className="font-semibold text-gray-800">
                    {currentStageData?.title}
                  </h4>
                  <Badge variant="secondary" className="text-xs">
                    {Math.round(stageProgress)}%
                  </Badge>
                </div>
                <p className="text-sm text-gray-600">
                  {currentStageData?.description}
                </p>
              </div>
            </div>

            {/* Stage Progress */}
            <div className="space-y-2">
              <Progress value={stageProgress} className="h-2" />
              <div className="flex justify-between text-xs text-gray-500">
                <span>Stage {currentStage + 1} of {loadingStages.length}</span>
                <span>{Math.round(progress)}% Complete</span>
              </div>
            </div>
          </div>

          {/* Stage Timeline */}
          <div className="space-y-3">
            <h5 className="text-sm font-medium text-gray-700">Processing Pipeline:</h5>
            <div className="space-y-2">
              {loadingStages.map((stage, index) => {
                const isCompleted = completedStages.has(index)
                const isCurrent = index === currentStage
                const isPending = index > currentStage

                return (
                  <div
                    key={stage.id}
                    className={`flex items-center space-x-3 p-2 rounded-lg transition-all duration-300 ${
                      isCurrent ? 'bg-blue-100 border border-blue-200' : 
                      isCompleted ? 'bg-green-50 border border-green-200' : 
                      'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center ${
                      isCompleted ? 'bg-green-500' : 
                      isCurrent ? 'bg-blue-500' : 
                      'bg-gray-300'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-4 h-4 text-white" />
                      ) : isCurrent ? (
                        <Loader2 className="w-4 h-4 text-white animate-spin" />
                      ) : (
                        <div className="w-2 h-2 bg-white rounded-full"></div>
                      )}
                    </div>
                    <div className="flex-1">
                      <div className={`text-sm font-medium ${
                        isCompleted ? 'text-green-700' : 
                        isCurrent ? 'text-blue-700' : 
                        'text-gray-500'
                      }`}>
                        {stage.title}
                      </div>
                    </div>
                    {isCurrent && (
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Overall Progress */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Overall Progress</span>
              <span className="text-sm font-bold text-blue-600">{Math.round(progress)}%</span>
            </div>
            <Progress value={progress} className="h-3" />
          </div>

          {/* Estimated Time */}
          <div className="text-center">
            <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
              <Zap className="w-3 h-3" />
              <span>Estimated completion: {Math.max(0, Math.round((100 - progress) / 10))}s</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
} 