"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { 
  Sparkles, 
  Download, 
  Copy, 
  RefreshCw, 
  Image as ImageIcon,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2,
  Trash2,
  Plus,
  X
} from "lucide-react"
import { toast } from "sonner"
import Image from "next/image"
import Link from "next/link"
import { ProtectedRoute } from "@/components/protected-route"

import { 
  apiClient, 
  type GenerateRequest, 
  type GeneratedImage, 
  type BatchStatusResponse 
} from "@/lib/api"

interface BatchRequest {
  id: string
  prompt: string
  negative_prompt?: string
  num_images: number
  size: string
  guidance_scale: number
  seed?: number
}

export default function BatchPage() {
  const [requests, setRequests] = useState<BatchRequest[]>([
    {
      id: "1",
      prompt: "",
      num_images: 1,
      size: "1024x1024",
      guidance_scale: 7.5
    }
  ])
  
  const [batchJobs, setBatchJobs] = useState<BatchStatusResponse[]>([])
  const [selectedJob, setSelectedJob] = useState<BatchStatusResponse | null>(null)
  const [isCreating, setIsCreating] = useState(false)
  const [isPolling, setIsPolling] = useState(false)

  // Load recent batch jobs on mount
  useEffect(() => {
    loadBatchJobs()
  }, [])

  const loadBatchJobs = async () => {
    try {
      const jobs = await apiClient.listBatchJobs(10)
      setBatchJobs(jobs)
    } catch (error) {
      console.error("Failed to load batch jobs:", error)
    }
  }

  const addRequest = () => {
    const newId = (requests.length + 1).toString()
    setRequests([
      ...requests,
      {
        id: newId,
        prompt: "",
        num_images: 1,
        size: "1024x1024",
        guidance_scale: 7.5
      }
    ])
  }

  const removeRequest = (id: string) => {
    if (requests.length > 1) {
      setRequests(requests.filter(req => req.id !== id))
    }
  }

  const updateRequest = (id: string, field: keyof BatchRequest, value: any) => {
    setRequests(requests.map(req => 
      req.id === id ? { ...req, [field]: value } : req
    ))
  }

  const createBatchJob = async () => {
    // Validate requests
    const validRequests = requests.filter(req => req.prompt.trim())
    if (validRequests.length === 0) {
      toast.error("Please add at least one valid request")
      return
    }

    if (validRequests.length > 50) {
      toast.error("Maximum 50 requests per batch")
      return
    }

    setIsCreating(true)

    try {
      const batchRequests: GenerateRequest[] = validRequests.map(req => ({
        prompt: req.prompt.trim(),
        negative_prompt: req.negative_prompt?.trim() || undefined,
        num_images: req.num_images,
        size: req.size,
        guidance_scale: req.guidance_scale,
        seed: req.seed
      }))

      const response = await apiClient.createBatchJob({
        requests: batchRequests,
        priority: "normal"
      })

      toast.success(`Batch job created: ${response.batch_id}`)
      
      // Start polling for status
      pollBatchStatus(response.batch_id)
      
      // Reload batch jobs list
      loadBatchJobs()
      
    } catch (error: any) {
      console.error("Failed to create batch job:", error)
      toast.error(error.message || "Failed to create batch job")
    } finally {
      setIsCreating(false)
    }
  }

  const pollBatchStatus = async (batchId: string) => {
    setIsPolling(true)
    
    try {
      await apiClient.pollBatchStatus(
        batchId,
        (status) => {
          setSelectedJob(status)
          // Update in batch jobs list
          setBatchJobs(prev => 
            prev.map(job => job.batch_id === batchId ? status : job)
          )
        },
        2000
      )
      
      toast.success("Batch job completed!")
    } catch (error) {
      console.error("Polling failed:", error)
      toast.error("Failed to track batch progress")
    } finally {
      setIsPolling(false)
    }
  }

  const cancelBatchJob = async (batchId: string) => {
    try {
      await apiClient.cancelBatchJob(batchId)
      toast.success("Batch job cancelled")
      loadBatchJobs()
    } catch (error: any) {
      console.error("Failed to cancel batch job:", error)
      toast.error(error.message || "Failed to cancel batch job")
    }
  }

  const downloadImage = async (image: GeneratedImage) => {
    try {
      const response = await fetch(image.presigned_url)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `snapbrand-${image.id}.png`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success("Image downloaded successfully!")
    } catch (error) {
      console.error("Download failed:", error)
      toast.error("Failed to download image")
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "bg-green-100 text-green-700"
      case "processing": return "bg-blue-100 text-blue-700"
      case "queued": return "bg-yellow-100 text-yellow-700"
      case "cancelled": return "bg-gray-100 text-gray-700"
      case "completed_with_errors": return "bg-orange-100 text-orange-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  imagifyy.ai
                </span>
              </Link>
              <Badge variant="secondary" className="bg-orange-100 text-orange-700">
                Batch Generate
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={loadBatchJobs}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Refresh
              </Button>
              <Button asChild>
                <Link href="/dashboard/generate">
                  <Sparkles className="w-4 h-4 mr-2" />
                  Single Generate
                </Link>
              </Button>
            </div>
          </div>
        </header>

        <div className="flex">
          {/* Main Content */}
          <main className="flex-1 p-6">
            <div className="max-w-6xl mx-auto space-y-6">
              {/* Batch Requests Form */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <span className="flex items-center">
                      <Zap className="w-5 h-5 mr-2" />
                      Batch Generation Requests
                    </span>
                    <Button variant="outline" size="sm" onClick={addRequest}>
                      <Plus className="w-4 h-4 mr-2" />
                      Add Request
                    </Button>
                  </CardTitle>
                  <CardDescription>
                    Create multiple image generation requests to process in batch
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {requests.map((request, index) => (
                    <Card key={request.id} className="border-2">
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-sm">Request {index + 1}</CardTitle>
                          {requests.length > 1 && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => removeRequest(request.id)}
                            >
                              <X className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div>
                          <Label>Prompt</Label>
                          <Textarea
                            placeholder="Describe the image you want to generate..."
                            value={request.prompt}
                            onChange={(e) => updateRequest(request.id, "prompt", e.target.value)}
                            rows={2}
                          />
                        </div>
                        
                        <div>
                          <Label>Negative Prompt (Optional)</Label>
                          <Textarea
                            placeholder="Describe what you don't want in the image..."
                            value={request.negative_prompt || ""}
                            onChange={(e) => updateRequest(request.id, "negative_prompt", e.target.value)}
                            rows={1}
                          />
                        </div>
                        
                        <div className="grid grid-cols-3 gap-4">
                          <div>
                            <Label>Images</Label>
                            <Input
                              type="number"
                              min="1"
                              max="10"
                              value={request.num_images}
                              onChange={(e) => updateRequest(request.id, "num_images", parseInt(e.target.value))}
                            />
                          </div>
                          <div>
                            <Label>Size</Label>
                            <select
                              value={request.size}
                              onChange={(e) => updateRequest(request.id, "size", e.target.value)}
                              className="w-full p-2 border rounded-md"
                            >
                              <option value="512x512">512x512</option>
                              <option value="768x768">768x768</option>
                              <option value="1024x1024">1024x1024</option>
                              <option value="1024x768">1024x768</option>
                              <option value="768x1024">768x1024</option>
                            </select>
                          </div>
                          <div>
                            <Label>Guidance Scale</Label>
                            <Input
                              type="number"
                              min="1"
                              max="20"
                              step="0.5"
                              value={request.guidance_scale}
                              onChange={(e) => updateRequest(request.id, "guidance_scale", parseFloat(e.target.value))}
                            />
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  
                  <Button 
                    onClick={createBatchJob} 
                    disabled={isCreating || requests.every(req => !req.prompt.trim())}
                    className="w-full"
                    size="lg"
                  >
                    {isCreating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Creating Batch Job...
                      </>
                    ) : (
                      <>
                        <Zap className="w-4 h-4 mr-2" />
                        Create Batch Job ({requests.filter(req => req.prompt.trim()).length} requests)
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Batch Jobs List */}
              {batchJobs.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Recent Batch Jobs</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {batchJobs.map((job) => (
                        <Card key={job.batch_id} className="border-2">
                          <CardHeader className="pb-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center space-x-2">
                                <Badge className={getStatusColor(job.status)}>
                                  {job.status}
                                </Badge>
                                <span className="text-sm font-medium">Batch {job.batch_id}</span>
                              </div>
                              <div className="flex items-center space-x-2">
                                {job.status === "processing" && (
                                  <Loader2 className="w-4 h-4 animate-spin" />
                                )}
                                {job.status === "completed" && (
                                  <CheckCircle className="w-4 h-4 text-green-600" />
                                )}
                                {job.status === "completed_with_errors" && (
                                  <AlertCircle className="w-4 h-4 text-orange-600" />
                                )}
                                {["queued", "processing"].includes(job.status) && (
                                  <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => cancelBatchJob(job.batch_id)}
                                  >
                                    <Trash2 className="w-4 h-4" />
                                  </Button>
                                )}
                              </div>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <div className="space-y-3">
                              <div className="flex items-center justify-between text-sm">
                                <span>Progress</span>
                                <span>{job.completed_requests}/{job.total_requests}</span>
                              </div>
                              <Progress value={job.progress} />
                              
                              <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                                <div>Created: {new Date(job.created_at).toLocaleString()}</div>
                                <div>Updated: {new Date(job.updated_at).toLocaleString()}</div>
                                {job.error_count > 0 && (
                                  <div className="text-orange-600">Errors: {job.error_count}</div>
                                )}
                              </div>
                              
                              {/* Show results if completed */}
                              {job.results && job.results.length > 0 && (
                                <div className="mt-4">
                                  <h4 className="text-sm font-medium mb-2">Generated Images</h4>
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                                    {job.results.flatMap(result => 
                                      result.images.map(image => (
                                        <div key={image.id} className="relative group">
                                          <Image
                                            src={image.presigned_url}
                                            alt={image.prompt}
                                            width={100}
                                            height={100}
                                            className="rounded-md object-cover"
                                          />
                                          <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                            <Button
                                              size="sm"
                                              variant="secondary"
                                              onClick={() => downloadImage(image)}
                                            >
                                              <Download className="w-3 h-3" />
                                            </Button>
                                          </div>
                                        </div>
                                      ))
                                    )}
                                  </div>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </main>
        </div>
      </div>
    </ProtectedRoute>
  )
}
