"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ProtectedRoute } from "@/components/protected-route"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import {
  Plus,
  ImageIcon,
  Palette,
  Zap,
  Download,
  Settings,
  BarChart3,
  Sparkles,
  Grid3X3,
  Filter,
  Search,
  MoreHorizontal,
  Loader2,
  X,
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useAuth } from "@/components/auth-context"
import { apiClient, type GeneratedImage, type BatchStatusResponse } from "@/lib/api"
import { toast } from "sonner"
import { Label } from "@/components/ui/label"

interface UserStats {
  total_images: number
  total_cost_spent: string
  credits?: {
    used: number
    remaining: number
    limit: number
    cost_per_credit: number
  }
  template_usage: Record<string, number>
  size_usage: Record<string, number>
}

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview")
  const [userStats, setUserStats] = useState<UserStats | null>(null)
  const [recentImages, setRecentImages] = useState<GeneratedImage[]>([])
  const [recentBatches, setRecentBatches] = useState<BatchStatusResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const { user } = useAuth()
  const [isViewingImage, setIsViewingImage] = useState<GeneratedImage | null>(null)

  // Load dashboard data
  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setIsLoading(true)
      
      // Load user statistics, recent images, and recent batches in parallel
      const [statsResponse, imagesResponse, batchesResponse] = await Promise.all([
        apiClient.getImageStats().catch(() => null),
        apiClient.listUserImages({ limit: 5 }).catch(() => []),
        apiClient.listBatchJobs(5).catch(() => [])
      ])

      if (statsResponse) setUserStats(statsResponse)
      setRecentImages(imagesResponse)
      setRecentBatches(batchesResponse)
      
    } catch (error) {
      console.error("Failed to load dashboard data:", error)
      toast.error("Failed to load dashboard data")
    } finally {
      setIsLoading(false)
    }
  }

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
    
    if (diffHours < 1) return "Just now"
    if (diffHours < 24) return `${diffHours} hours ago`
    if (diffDays === 1) return "1 day ago"
    return `${diffDays} days ago`
  }

  const getTemplateDisplayName = (templateId: string | null) => {
    if (!templateId) return "Custom"
    
    const templateNames: Record<string, string> = {
      "product-hero": "Product Hero",
      "instagram-post": "Instagram Post",
      "email-header": "Email Header",
      "website-banner": "Website Banner",
      "linkedin-post": "LinkedIn Post",
    }
    
    return templateNames[templateId] || templateId
  }

  const getCategoryFromTemplate = (templateId: string | null) => {
    if (!templateId) return "Custom"
    
    const templateCategories: Record<string, string> = {
      "product-hero": "E-commerce",
      "instagram-post": "Social Media",
      "email-header": "Marketing",
      "website-banner": "Web",
      "linkedin-post": "Social Media",
    }
    
    return templateCategories[templateId] || "Custom"
  }

  const handleDownloadImage = async (image: GeneratedImage) => {
    try {
      const response = await fetch(image.presigned_url)
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = `${image.prompt.substring(0, 30).replace(/[^a-zA-Z0-9]/g, '_')}_${image.id}.png`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      toast.success("Image downloaded successfully")
    } catch (error) {
      console.error('Download failed:', error)
      toast.error("Failed to download image")
    }
  }

  const handleViewDetails = (image: GeneratedImage) => {
    setIsViewingImage(image)
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Link href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SnapBrand.ai
              </span>
            </Link>
            <Badge variant="secondary" className="bg-green-100 text-green-700">
              {user?.is_premium ? "Pro Plan" : "Free Plan"}
            </Badge>
          </div>
          <div className="flex items-center space-x-4">
            <Button variant="outline" size="sm">
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button asChild>
              <Link href="/dashboard/generate">
                <Plus className="w-4 h-4 mr-2" />
                Generate Images
              </Link>
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 bg-white border-r min-h-screen">
          <nav className="p-6">
            <ul className="space-y-2">
              <li>
                <Button
                  variant={activeTab === "overview" ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setActiveTab("overview")}
                >
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Overview
                </Button>
              </li>
              <li>
                <Button
                  variant={activeTab === "generate" ? "default" : "ghost"}
                  className="w-full justify-start"
                  asChild
                >
                  <Link href="/dashboard/generate">
                    <Zap className="w-4 h-4 mr-2" />
                    Generate
                  </Link>
                </Button>
              </li>
              <li>
                <Button
                  variant={activeTab === "gallery" ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setActiveTab("gallery")}
                >
                  <ImageIcon className="w-4 h-4 mr-2" />
                  Gallery
                </Button>
              </li>
              <li>
                <Button
                  variant={activeTab === "brand-assets" ? "default" : "ghost"}
                  className="w-full justify-start"
                  asChild
                >
                  <Link href="/dashboard/brand-assets">
                    <Palette className="w-4 h-4 mr-2" />
                    Brand Assets
                  </Link>
                </Button>
              </li>
              <li>
                <Button
                  variant={activeTab === "templates" ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setActiveTab("templates")}
                >
                  <Grid3X3 className="w-4 h-4 mr-2" />
                  Templates
                </Button>
              </li>
            </ul>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === "overview" && (
            <div className="space-y-6">
              {isLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
                  <span className="ml-2 text-gray-600">Loading dashboard...</span>
                </div>
              ) : (
                <>
                  {/* Stats Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Images Generated</CardTitle>
                        <ImageIcon className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{userStats?.total_images || 0}</div>
                        <p className="text-xs text-muted-foreground">Total images created</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Credits Used</CardTitle>
                        <Zap className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{userStats?.credits?.used || 0}</div>
                        <p className="text-xs text-muted-foreground">{userStats?.credits?.remaining || 0} remaining</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Cost</CardTitle>
                        <BarChart3 className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">${parseFloat(userStats?.total_cost_spent || "0").toFixed(2)}</div>
                        <p className="text-xs text-muted-foreground">Lifetime spending</p>
                      </CardContent>
                    </Card>
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Recent Batches</CardTitle>
                        <Grid3X3 className="h-4 w-4 text-muted-foreground" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{recentBatches.length}</div>
                        <p className="text-xs text-muted-foreground">Last 5 batch jobs</p>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Recent Activity */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Recent Activity</CardTitle>
                      <CardDescription>Your latest image generations and downloads</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {recentImages.length === 0 ? (
                          <div className="text-center py-8 text-gray-500">
                            <ImageIcon className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                            <p>No images generated yet</p>
                            <p className="text-sm">Create your first image to see activity here</p>
                          </div>
                        ) : (
                          recentImages.map((image) => (
                            <div key={image.id} className="flex items-center justify-between p-4 border rounded-lg">
                              <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 rounded-lg overflow-hidden bg-gray-100">
                                  <Image
                                    src={image.presigned_url}
                                    alt={image.prompt}
                                    width={48}
                                    height={48}
                                    className="w-full h-full object-cover"
                                  />
                                </div>
                                <div>
                                  <h3 className="font-medium truncate max-w-xs">
                                    {image.prompt.length > 50 ? `${image.prompt.substring(0, 50)}...` : image.prompt}
                                  </h3>
                                  <p className="text-sm text-gray-500">
                                    {getCategoryFromTemplate(image.metadata?.template_id || null)} • {formatTimeAgo(image.created_at)}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge variant="default">completed</Badge>
                                <Badge variant="outline">{image.size}</Badge>
                                <DropdownMenu>
                                  <DropdownMenuTrigger asChild>
                                    <Button variant="ghost" size="sm">
                                      <MoreHorizontal className="w-4 h-4" />
                                    </Button>
                                  </DropdownMenuTrigger>
                                  <DropdownMenuContent>
                                    <DropdownMenuItem onClick={() => handleDownloadImage(image)}>
                                      <Download className="w-4 h-4 mr-2" />
                                      Download
                                    </DropdownMenuItem>
                                    <DropdownMenuItem onClick={() => handleViewDetails(image)}>
                                      View Details
                                    </DropdownMenuItem>
                                  </DropdownMenuContent>
                                </DropdownMenu>
                              </div>
                            </div>
                          ))
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recent Batch Jobs */}
                  {recentBatches.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle>Recent Batch Jobs</CardTitle>
                        <CardDescription>Your latest batch generation jobs</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-4">
                          {recentBatches.map((batch) => (
                            <div key={batch.batch_id} className="flex items-center justify-between p-4 border rounded-lg">
                              <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-gradient-to-br from-orange-100 to-red-100 rounded-lg flex items-center justify-center">
                                  <Zap className="w-6 h-6 text-orange-600" />
                                </div>
                                <div>
                                  <h3 className="font-medium">Batch {batch.batch_id}</h3>
                                  <p className="text-sm text-gray-500">
                                    {batch.completed_requests}/{batch.total_requests} requests • {formatTimeAgo(batch.updated_at)}
                                  </p>
                                </div>
                              </div>
                              <div className="flex items-center space-x-2">
                                <Badge variant={
                                  batch.status === "completed" ? "default" :
                                  batch.status === "processing" ? "secondary" :
                                  batch.status === "queued" ? "outline" : "destructive"
                                }>
                                  {batch.status}
                                </Badge>
                                <Button variant="outline" size="sm" asChild>
                                  <Link href="/dashboard/batch">
                                    View
                                  </Link>
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </>
              )}
            </div>
          )}

          {/* Gallery Tab */}
          {activeTab === "gallery" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold">Gallery</h1>
                  <p className="text-gray-600">Browse and manage your generated images</p>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input placeholder="Search images..." className="pl-10" />
                  </div>
                  <Button variant="outline">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {recentImages.map((image) => (
                  <Card key={image.id} className="overflow-hidden">
                    <div className="relative aspect-square">
                      <Image
                        src={image.presigned_url}
                        alt={image.prompt}
                        fill
                        className="object-cover"
                      />
                    </div>
                    <CardContent className="p-4">
                      <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                        {image.prompt}
                      </p>
                      <div className="flex items-center justify-between">
                        <Badge variant="outline" className="text-xs">
                          {image.size}
                        </Badge>
                        <span className="text-xs text-gray-500">
                          {formatTimeAgo(image.created_at)}
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {/* Templates Tab - Keep existing mock data for now */}
          {activeTab === "templates" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold">Templates</h1>
                  <p className="text-gray-600">Choose from pre-designed templates to speed up your workflow</p>
                </div>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Create Template
                </Button>
              </div>

              <Tabs defaultValue="all" className="w-full">
                <TabsList>
                  <TabsTrigger value="all">All Templates</TabsTrigger>
                  <TabsTrigger value="ecommerce">E-commerce</TabsTrigger>
                  <TabsTrigger value="social">Social Media</TabsTrigger>
                  <TabsTrigger value="marketing">Marketing</TabsTrigger>
                </TabsList>

                <TabsContent value="all" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {/* Template cards would go here - keeping simplified for now */}
                    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">Product Hero Shot</CardTitle>
                          <Badge variant="outline">E-commerce</Badge>
                        </div>
                        <CardDescription>Professional product photography</CardDescription>
                      </CardHeader>
                      <CardContent>
                        <div className="w-full h-32 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center">
                          <ImageIcon className="w-8 h-8 text-blue-600" />
                        </div>
                        <Button className="w-full" asChild>
                          <Link href="/dashboard/generate">Use Template</Link>
                        </Button>
                      </CardContent>
                    </Card>
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </main>
      </div>

      {/* Image Details Modal */}
      {isViewingImage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" onClick={() => setIsViewingImage(null)}>
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto m-4" onClick={(e) => e.stopPropagation()}>
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold">Image Details</h2>
                <Button variant="ghost" size="sm" onClick={() => setIsViewingImage(null)}>
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <div className="aspect-square relative bg-gray-100 rounded-lg overflow-hidden">
                    <Image
                      src={isViewingImage.presigned_url}
                      alt={isViewingImage.prompt}
                      fill
                      className="object-cover"
                    />
                  </div>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <Label className="text-sm font-medium text-gray-500">Prompt</Label>
                    <p className="mt-1 text-sm">{isViewingImage.prompt}</p>
                  </div>
                  
                  {isViewingImage.metadata?.negative_prompt && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Negative Prompt</Label>
                      <p className="mt-1 text-sm">{isViewingImage.metadata.negative_prompt}</p>
                    </div>
                  )}
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Size</Label>
                      <p className="mt-1 text-sm">{isViewingImage.size}</p>
                    </div>
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Created</Label>
                      <p className="mt-1 text-sm">{formatTimeAgo(isViewingImage.created_at)}</p>
                    </div>
                  </div>
                  
                  {isViewingImage.metadata?.guidance_scale && (
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label className="text-sm font-medium text-gray-500">Guidance Scale</Label>
                        <p className="mt-1 text-sm">{isViewingImage.metadata.guidance_scale}</p>
                      </div>
                      {isViewingImage.metadata?.seed && (
                        <div>
                          <Label className="text-sm font-medium text-gray-500">Seed</Label>
                          <p className="mt-1 text-sm">{isViewingImage.metadata.seed}</p>
                        </div>
                      )}
                    </div>
                  )}
                  
                  {isViewingImage.metadata?.generation_cost && (
                    <div>
                      <Label className="text-sm font-medium text-gray-500">Generation Cost</Label>
                      <p className="mt-1 text-sm">${parseFloat(isViewingImage.metadata.generation_cost).toFixed(4)}</p>
                    </div>
                  )}
                  
                  <div className="flex space-x-2 pt-4">
                    <Button onClick={() => handleDownloadImage(isViewingImage)} className="flex-1">
                      <Download className="w-4 h-4 mr-2" />
                      Download
                    </Button>
                    <Button variant="outline" onClick={() => setIsViewingImage(null)} className="flex-1">
                      Close
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </ProtectedRoute>
  )
}
