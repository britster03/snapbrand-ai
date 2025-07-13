"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Upload, Palette, Target, TrendingUp, Users, Download, Trash2, Eye, AlertCircle, Sparkles, BarChart3, Shield, Zap, Star, Award, Brain, Camera, Lightbulb, Edit, Settings, Share2, ExternalLink } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Separator } from "@/components/ui/separator"
import { useToast } from "@/components/ui/use-toast"
import { AuthUtils } from "@/lib/auth-utils"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface BrandProfile {
  id: number
  name: string
  description?: string
  industry: string
  visual_style?: string
  primary_colors: string[]
  secondary_colors: string[]
  brand_keywords: string[]
  total_generations: number
  successful_campaigns: number
  avg_engagement_rate: number
}

interface BrandAsset {
  id: number
  asset_type: string
  asset_name: string
  asset_url: string
  dominant_colors?: any[]
  style_attributes?: any
  analysis_completed: boolean
  created_at: string
  file_size?: number
  dimensions?: { width: number; height: number }
}

interface BrandInsights {
  brand_profile: any
  color_insights: any
  style_insights: any
  asset_insights: any
  recommendations: string[]
}

const industryIcons = {
  "e-commerce": "🛒",
  "saas": "💻",
  "healthcare": "🏥",
  "finance": "💰",
  "education": "📚",
  "real-estate": "🏠",
  "retail": "🏪",
  "hospitality": "☕",
  "technology": "⚡",
  "fashion": "👕",
  "food": "🍔",
  "automotive": "🚗",
  "other": "🔧"
}

const visualStyleConfig = {
  "modern": { emoji: "✨", gradient: "from-blue-500 to-cyan-500" },
  "classic": { emoji: "🎩", gradient: "from-amber-500 to-orange-500" },
  "bold": { emoji: "🔥", gradient: "from-red-500 to-pink-500" },
  "playful": { emoji: "🎨", gradient: "from-purple-500 to-pink-500" },
  "professional": { emoji: "💼", gradient: "from-slate-500 to-gray-600" },
  "minimal": { emoji: "⚪", gradient: "from-gray-400 to-slate-500" },
  "luxury": { emoji: "👑", gradient: "from-yellow-500 to-amber-500" }
}

export default function BrandDetailPage() {
  const params = useParams()
  const router = useRouter()
  const brandId = params.brandId as string
  const { toast } = useToast()

  const [brand, setBrand] = useState<BrandProfile | null>(null)
  const [assets, setAssets] = useState<BrandAsset[]>([])
  const [insights, setInsights] = useState<BrandInsights | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [activeTab, setActiveTab] = useState("overview")

  // Add state for campaigns and campaign dialog
  const [campaigns, setCampaigns] = useState<any[]>([])
  const [campaignDialogOpen, setCampaignDialogOpen] = useState(false)
  const [creatingCampaign, setCreatingCampaign] = useState(false)
  const [newCampaign, setNewCampaign] = useState({
    name: "",
    description: "",
    campaign_type: "",
    start_date: "",
    end_date: "",
    target_platforms: "",
    target_metrics: ""
  })

  // Add state for campaign metrics
  const [metrics, setMetrics] = useState({ engagement_rate: '', conversion_rate: '', reach: '' })

  // Update newCampaign reset to clear metrics too
  const resetNewCampaign = () => {
    setNewCampaign({ name: '', description: '', campaign_type: '', start_date: '', end_date: '', target_platforms: '', target_metrics: '' })
    setMetrics({ engagement_rate: '', conversion_rate: '', reach: '' })
  }

  useEffect(() => {
    fetchBrandData()
  }, [brandId])

  // Fetch campaigns
  const fetchCampaigns = async () => {
    try {
      const token = AuthUtils.getToken()
      if (!token) return
      const headers = { Authorization: `Bearer ${token}` }
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}/campaigns`, { headers })
      if (response.ok) {
        const data = await response.json()
        setCampaigns(data)
      }
    } catch (e) { /* ignore */ }
  }

  useEffect(() => {
    fetchCampaigns()
  }, [brandId])

  // Create campaign handler
  const handleCreateCampaign = async () => {
    if (!newCampaign.name.trim()) {
      toast({
        title: "Validation Error",
        description: "Campaign name is required.",
        variant: "destructive"
      })
      return
    }
    setCreatingCampaign(true)
    try {
      const token = AuthUtils.getToken()
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "You must be logged in to create a campaign.",
          variant: "destructive"
        })
        setCreatingCampaign(false)
        return
      }
      const headers = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" }
      // Build metrics object from state, only include filled fields
      const target_metrics = Object.fromEntries(
        Object.entries(metrics).filter(([_, v]) => v !== '' && !isNaN(Number(v))).map(([k, v]) => [k, Number(v)])
      )
      const body = JSON.stringify({
        ...newCampaign,
        target_platforms: newCampaign.target_platforms.split(",").map((s) => s.trim()),
        target_metrics
      })
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}/campaigns`, {
        method: "POST",
        headers,
        body
      })
      if (response.ok) {
        setCampaignDialogOpen(false)
        resetNewCampaign()
        fetchCampaigns()
        toast({ title: "Campaign created!" })
      } else {
        let errorMsg = "Failed to create campaign"
        try {
          const errorData = await response.json()
          if (errorData && errorData.detail) errorMsg = errorData.detail
        } catch {}
        toast({ title: "Error", description: errorMsg, variant: "destructive" })
      }
    } catch (e: any) {
      toast({ title: "Error", description: e?.message || "Failed to create campaign", variant: "destructive" })
    } finally {
      setCreatingCampaign(false)
    }
  }

  const fetchBrandData = async () => {
    try {
      const token = AuthUtils.getToken()
      
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      const headers = { Authorization: `Bearer ${token}` }
      
      // Fetch brand profile
      const brandResponse = await fetch(`${API_URL}/brands/profiles/${brandId}`, {
        headers,
      })

      if (brandResponse.status === 401) {
        AuthUtils.clearAuth()
        router.push("/login")
        return
      }

      if (brandResponse.ok) {
        const brandData = await brandResponse.json()
        setBrand(brandData)
      }

      // Fetch brand assets
      const assetsResponse = await fetch(`${API_URL}/brands/profiles/${brandId}/assets`, {
        headers,
      })

      if (assetsResponse.ok) {
        const assetsData = await assetsResponse.json()
        setAssets(assetsData)
      }

      // Fetch brand insights
      const insightsResponse = await fetch(`${API_URL}/brands/profiles/${brandId}/insights`, {
        headers,
      })

      if (insightsResponse.ok) {
        const insightsData = await insightsResponse.json()
        setInsights(insightsData)
      }
    } catch (error) {
      console.error("Error fetching brand data:", error)
      toast({
        title: "Error",
        description: "Failed to load brand data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAssetUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append("file", file)
    formData.append("asset_type", "logo")
    formData.append("asset_name", file.name)

    try {
      const token = AuthUtils.getToken()
      
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}/assets`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      })

      if (response.status === 401) {
        AuthUtils.clearAuth()
        router.push("/login")
        return
      }

      if (response.ok) {
        toast({
          title: "🎉 Success!",
          description: "Asset uploaded and analyzed successfully",
        })
        setUploadDialogOpen(false)
        fetchBrandData()
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to upload asset",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error uploading asset:", error)
      toast({
        title: "Error",
        description: "Failed to upload asset",
        variant: "destructive",
      })
    } finally {
      setUploading(false)
    }
  }

  const deleteAsset = async (assetId: number) => {
    if (!confirm("Are you sure you want to delete this asset?")) return

    try {
      const token = AuthUtils.getToken()
      
      if (!token) {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}/assets/${assetId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })

      if (response.status === 401) {
        AuthUtils.clearAuth()
        router.push("/login")
        return
      }

      if (response.ok) {
        toast({
          title: "Success",
          description: "Asset deleted successfully",
        })
        fetchBrandData()
      } else {
        toast({
          title: "Error",
          description: "Failed to delete asset",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error deleting asset:", error)
      toast({
        title: "Error",
        description: "Failed to delete asset",
        variant: "destructive",
      })
    }
  }

  if (loading || !brand) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
          <Sparkles className="w-6 h-6 text-primary absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" />
        </div>
        <p className="mt-4 text-muted-foreground animate-pulse">Loading brand details...</p>
      </div>
    )
  }

  const styleInfo = brand.visual_style ? visualStyleConfig[brand.visual_style as keyof typeof visualStyleConfig] : null
  const industryEmoji = industryIcons[brand.industry as keyof typeof industryIcons] || industryIcons.other

  return (
    <div className="container mx-auto py-8 space-y-8">
      {/* Navigation */}
      <Button
        variant="ghost"
        onClick={() => router.push("/dashboard/brands")}
        className="hover:bg-muted/50 transition-colors"
      >
        <ArrowLeft className="mr-2 h-4 w-4" />
        Back to Brands
      </Button>

      {/* Brand Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-900 dark:to-gray-900 border">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-400/5 via-gray-400/10 to-transparent opacity-30"></div>
        <div className="relative p-8">
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-6">
              <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-950 dark:to-purple-950 flex items-center justify-center shadow-lg border border-white/50">
                <span className="text-3xl">{industryEmoji}</span>
              </div>
              <div className="space-y-3">
                <div className="space-y-2">
                  <h1 className="text-4xl font-bold tracking-tight">{brand.name}</h1>
                  {brand.description && (
                    <p className="text-lg text-muted-foreground max-w-2xl leading-relaxed">
                      {brand.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center space-x-3">
                  <Badge variant="secondary" className="font-medium">
                    {industryEmoji} {brand.industry.replace("-", " ")}
                  </Badge>
                  {styleInfo && (
                    <Badge variant="outline" className="border-primary/20">
                      {styleInfo.emoji} {brand.visual_style}
                    </Badge>
                  )}
                  {brand.brand_keywords.length > 0 && (
                    <Badge variant="outline" className="border-muted-foreground/20">
                      {brand.brand_keywords.length} keyword{brand.brand_keywords.length !== 1 ? 's' : ''}
                    </Badge>
                  )}
                </div>
              </div>
            </div>
            <div className="flex flex-col space-y-3">
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/dashboard/brands/${brandId}/edit`)}
                  className="hover:bg-primary/5"
                >
                  <Edit className="mr-2 h-4 w-4" />
                  Edit Profile
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => router.push(`/dashboard/brands/${brandId}/assets`)}
                  className="hover:bg-primary/5"
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Manage Assets
                </Button>
              </div>
              <Button
                size="lg"
                onClick={() => router.push(`/dashboard/generate?brand=${brandId}`)}
                className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 shadow-lg"
              >
                <Sparkles className="mr-2 h-5 w-5" />
                Generate Content
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-6 md:grid-cols-3">
        <Card className="relative overflow-hidden border-0 bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-blue-400/10 to-cyan-400/10 rounded-full -mr-10 -mt-10"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Total Generations</p>
                <p className="text-3xl font-bold text-blue-600">{brand.total_generations}</p>
                <p className="text-xs text-muted-foreground">AI-generated images</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-blue-100 dark:bg-blue-950/30 flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-0 bg-gradient-to-br from-emerald-50 to-green-50 dark:from-emerald-950/20 dark:to-green-950/20">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-emerald-400/10 to-green-400/10 rounded-full -mr-10 -mt-10"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Successful Campaigns</p>
                <p className="text-3xl font-bold text-emerald-600">{brand.successful_campaigns}</p>
                <p className="text-xs text-muted-foreground">Marketing campaigns</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-emerald-100 dark:bg-emerald-950/30 flex items-center justify-center">
                <Target className="w-6 h-6 text-emerald-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="relative overflow-hidden border-0 bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20">
          <div className="absolute top-0 right-0 w-20 h-20 bg-gradient-to-br from-amber-400/10 to-orange-400/10 rounded-full -mr-10 -mt-10"></div>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div className="space-y-2">
                <p className="text-sm font-medium text-muted-foreground">Engagement Rate</p>
                <p className="text-3xl font-bold text-amber-600">{brand.avg_engagement_rate}%</p>
                <p className="text-xs text-muted-foreground">Average performance</p>
              </div>
              <div className="w-12 h-12 rounded-xl bg-amber-100 dark:bg-amber-950/30 flex items-center justify-center">
                <Users className="w-6 h-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-8">
        <TabsList className="flex w-full overflow-x-auto h-12 bg-muted/30 space-x-2">
          <TabsTrigger value="overview" className="flex-shrink-0 data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Eye className="w-4 h-4 mr-2" />
            Overview
          </TabsTrigger>
          <TabsTrigger value="assets" className="flex-shrink-0 data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Upload className="w-4 h-4 mr-2" />
            Assets ({assets.length})
          </TabsTrigger>
          <TabsTrigger value="guidelines" className="flex-shrink-0 data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Shield className="w-4 h-4 mr-2" />
            Guidelines
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex-shrink-0 data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <BarChart3 className="w-4 h-4 mr-2" />
            Analytics
          </TabsTrigger>
          <TabsTrigger value="campaigns" className="flex-shrink-0 data-[state=active]:bg-background data-[state=active]:shadow-sm">
            <Target className="w-4 h-4 mr-2" />
            Campaigns
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-8">
          <div className="grid gap-8 lg:grid-cols-2">
            {/* Brand Colors */}
            <Card className="border-0 shadow-lg">
              <CardHeader className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-pink-100 to-purple-100 dark:from-pink-950 dark:to-purple-950 flex items-center justify-center">
                    <Palette className="w-4 h-4 text-pink-600" />
                  </div>
                  <CardTitle>Brand Colors</CardTitle>
                </div>
                <CardDescription>Your brand's visual identity palette</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {brand.primary_colors && brand.primary_colors.length > 0 ? (
                  <div className="space-y-6">
                    <div className="space-y-3">
                      <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Primary Colors</Label>
                      <div className="grid grid-cols-4 gap-3">
                        {brand.primary_colors.map((color, index) => (
                          <div key={index} className="group space-y-2">
                            <div
                              className="w-full h-16 rounded-xl border-2 border-white shadow-lg ring-1 ring-black/5 group-hover:scale-105 transition-transform duration-200 cursor-pointer"
                              style={{ backgroundColor: color }}
                              title={color}
                            />
                            <span className="text-xs font-mono text-center block text-muted-foreground">{color}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                    {brand.secondary_colors && brand.secondary_colors.length > 0 && (
                      <div className="space-y-3">
                        <Label className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">Secondary Colors</Label>
                        <div className="grid grid-cols-4 gap-3">
                          {brand.secondary_colors.map((color, index) => (
                            <div key={index} className="group space-y-2">
                              <div
                                className="w-full h-16 rounded-xl border-2 border-white shadow-lg ring-1 ring-black/5 group-hover:scale-105 transition-transform duration-200 cursor-pointer"
                                style={{ backgroundColor: color }}
                                title={color}
                              />
                              <span className="text-xs font-mono text-center block text-muted-foreground">{color}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
                      <Palette className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <p className="text-muted-foreground mb-4">
                      No colors defined yet. Upload brand assets to extract colors automatically.
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => setActiveTab("assets")}
                      className="hover:bg-primary/5"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Assets
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Brand Keywords */}
            <Card className="border-0 shadow-lg">
              <CardHeader className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-950 dark:to-indigo-950 flex items-center justify-center">
                    <Lightbulb className="w-4 h-4 text-blue-600" />
                  </div>
                  <CardTitle>Brand Keywords</CardTitle>
                </div>
                <CardDescription>Words that define your brand personality</CardDescription>
              </CardHeader>
              <CardContent>
                {brand.brand_keywords && brand.brand_keywords.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {brand.brand_keywords.map((keyword, index) => (
                      <Badge key={index} variant="secondary" className="px-3 py-1 text-sm">
                        {keyword}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
                      <Lightbulb className="w-8 h-8 text-muted-foreground" />
                    </div>
                    <p className="text-muted-foreground mb-4">
                      No keywords defined yet. Add keywords to help AI understand your brand personality.
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => router.push(`/dashboard/brands/${brandId}/edit`)}
                      className="hover:bg-primary/5"
                    >
                      <Edit className="w-4 h-4 mr-2" />
                      Add Keywords
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* AI Recommendations */}
          {insights?.recommendations && insights.recommendations.length > 0 && (
            <Card className="border-0 shadow-lg">
              <CardHeader className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-100 to-green-100 dark:from-emerald-950 dark:to-green-950 flex items-center justify-center">
                    <Brain className="w-4 h-4 text-emerald-600" />
                  </div>
                  <CardTitle>AI Recommendations</CardTitle>
                </div>
                <CardDescription>Smart suggestions to improve your brand consistency</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {insights.recommendations.map((recommendation, index) => (
                    <Alert key={index} className="border-emerald-200 bg-emerald-50/50 dark:border-emerald-800 dark:bg-emerald-950/20">
                      <Lightbulb className="h-4 w-4 text-emerald-600" />
                      <AlertDescription className="text-sm leading-relaxed">
                        {recommendation}
                      </AlertDescription>
                    </Alert>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="assets" className="space-y-8">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Brand Assets</h2>
              <p className="text-muted-foreground">Upload and manage your brand's visual assets</p>
            </div>
            <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700">
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Asset
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-md">
                <DialogHeader className="space-y-3">
                  <DialogTitle className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center">
                      <Upload className="w-4 h-4 text-white" />
                    </div>
                    <span>Upload Brand Asset</span>
                  </DialogTitle>
                  <DialogDescription>
                    Upload logos, images, or other brand assets for AI-powered analysis and color extraction.
                  </DialogDescription>
                </DialogHeader>
                <Separator />
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="asset-upload" className="text-sm font-semibold">Select File</Label>
                    <Input
                      id="asset-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleAssetUpload}
                      disabled={uploading}
                      className="mt-2"
                    />
                  </div>
                  {uploading && (
                    <div className="flex items-center space-x-3 p-4 bg-muted/50 rounded-lg">
                      <div className="w-8 h-8 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
                      <div className="space-y-1">
                        <p className="text-sm font-medium">Uploading and analyzing...</p>
                        <p className="text-xs text-muted-foreground">This may take a few moments</p>
                      </div>
                    </div>
                  )}
                </div>
              </DialogContent>
            </Dialog>
          </div>

          {assets.length === 0 ? (
            <Card className="border-2 border-dashed border-muted-foreground/25 bg-muted/5">
              <CardContent className="flex flex-col items-center justify-center py-16 text-center space-y-6">
                <div className="w-20 h-20 rounded-full bg-gradient-to-br from-violet-100 to-purple-100 dark:from-violet-950 dark:to-purple-950 flex items-center justify-center">
                  <Camera className="w-10 h-10 text-violet-600" />
                </div>
                <div className="space-y-2">
                  <h3 className="text-xl font-semibold">No assets uploaded yet</h3>
                  <p className="text-muted-foreground max-w-md">
                    Upload your logo and brand assets to extract colors, analyze style attributes, and ensure brand consistency.
                  </p>
                </div>
                <Button 
                  onClick={() => setUploadDialogOpen(true)}
                  className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  Upload Your First Asset
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {assets.map((asset) => (
                <Card key={asset.id} className="group overflow-hidden border-0 shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-1">
                  <div className="aspect-square relative overflow-hidden">
                    <img
                      src={asset.asset_url}
                      alt={asset.asset_name}
                      className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                    />
                    <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors duration-300" />
                    {asset.analysis_completed && (
                      <Badge className="absolute top-3 right-3 bg-emerald-600 hover:bg-emerald-700">
                        <Sparkles className="w-3 h-3 mr-1" />
                        Analyzed
                      </Badge>
                    )}
                    <div className="absolute bottom-3 left-3 right-3 flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                      <Button
                        variant="secondary"
                        size="sm"
                        className="flex-1 bg-white/90 hover:bg-white"
                        onClick={() => window.open(asset.asset_url, "_blank")}
                      >
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                      <Button
                        variant="secondary"
                        size="sm"
                        className="bg-white/90 hover:bg-white text-destructive hover:text-destructive"
                        onClick={() => deleteAsset(asset.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <CardContent className="p-5 space-y-4">
                    <div>
                      <h4 className="font-semibold truncate">{asset.asset_name}</h4>
                      <p className="text-sm text-muted-foreground capitalize">{asset.asset_type.replace("-", " ")}</p>
                    </div>
                    
                    {asset.dominant_colors && asset.dominant_colors.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">Extracted Colors</span>
                        <div className="flex space-x-2">
                          {asset.dominant_colors.slice(0, 6).map((color, index) => (
                            <div
                              key={index}
                              className="w-8 h-8 rounded-lg border-2 border-white shadow-sm ring-1 ring-black/5"
                              style={{ backgroundColor: color.hex }}
                              title={`${color.hex} (${color.percentage}%)`}
                            />
                          ))}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="guidelines" className="space-y-8">
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold">Brand Guidelines</h2>
              <p className="text-muted-foreground">Automated rules and standards for brand consistency</p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-100 to-indigo-100 dark:from-blue-950 dark:to-indigo-950 flex items-center justify-center">
                        <Palette className="w-4 h-4 text-blue-600" />
                      </div>
                      <CardTitle className="text-lg">Primary Color Usage</CardTitle>
                    </div>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">Active</Badge>
                  </div>
                  <CardDescription>
                    Primary colors should dominate brand elements for consistency
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Minimum Coverage</span>
                      <span className="font-medium">60%</span>
                    </div>
                    <Progress value={60} className="h-3" />
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-950 dark:to-pink-950 flex items-center justify-center">
                        <Eye className="w-4 h-4 text-purple-600" />
                      </div>
                      <CardTitle className="text-lg">Visual Style Consistency</CardTitle>
                    </div>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">Active</Badge>
                  </div>
                  <CardDescription>
                    All content should match the {brand.visual_style || "defined"} visual style
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-3">
                    {styleInfo && (
                      <>
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${styleInfo.gradient} flex items-center justify-center`}>
                          <span className="text-xl">{styleInfo.emoji}</span>
                        </div>
                        <div>
                          <p className="font-medium capitalize">{brand.visual_style} Style</p>
                          <p className="text-sm text-muted-foreground">Automatically enforced</p>
                        </div>
                      </>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-amber-100 to-yellow-100 dark:from-amber-950 dark:to-yellow-950 flex items-center justify-center">
                        <Shield className="w-4 h-4 text-amber-600" />
                      </div>
                      <CardTitle className="text-lg">Logo Protection</CardTitle>
                    </div>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">Active</Badge>
                  </div>
                  <CardDescription>
                    Maintain proper clear space around logo elements
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      Minimum clear space: 2x logo height
                    </p>
                  </div>
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-100 to-emerald-100 dark:from-green-950 dark:to-emerald-950 flex items-center justify-center">
                        <Target className="w-4 h-4 text-green-600" />
                      </div>
                      <CardTitle className="text-lg">Brand Keyword Usage</CardTitle>
                    </div>
                    <Badge variant="secondary" className="bg-emerald-100 text-emerald-700">Active</Badge>
                  </div>
                  <CardDescription>
                    Generated content incorporates brand keywords naturally
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1">
                    {brand.brand_keywords.slice(0, 4).map((keyword, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {keyword}
                      </Badge>
                    ))}
                    {brand.brand_keywords.length > 4 && (
                      <Badge variant="outline" className="text-xs">
                        +{brand.brand_keywords.length - 4} more
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-8">
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold">Brand Analytics</h2>
              <p className="text-muted-foreground">Insights into your brand's visual consistency and performance</p>
            </div>

            <div className="grid gap-8 lg:grid-cols-2">
              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-100 to-cyan-100 dark:from-blue-950 dark:to-cyan-950 flex items-center justify-center">
                      <Palette className="w-4 h-4 text-blue-600" />
                    </div>
                    <CardTitle>Color Consistency</CardTitle>
                  </div>
                  <CardDescription>How well your content matches brand colors</CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {insights?.color_insights?.color_consistency_score !== undefined ? (
                    <>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium">Consistency Score</span>
                          <span className="text-2xl font-bold text-blue-600">
                            {(insights.color_insights.color_consistency_score * 100).toFixed(0)}%
                          </span>
                        </div>
                        <Progress value={insights.color_insights.color_consistency_score * 100} className="h-3" />
                      </div>
                      
                                              {insights?.color_insights?.detected_top_colors && (
                        <div className="space-y-3">
                          <span className="text-sm font-medium">Most Used Colors</span>
                          <div className="grid grid-cols-5 gap-2">
                            {insights.color_insights.detected_top_colors.slice(0, 5).map((color: any, index: number) => (
                              <div key={index} className="space-y-1">
                                <div
                                  className="w-full h-12 rounded-lg border-2 border-white shadow-sm ring-1 ring-black/5"
                                  style={{ backgroundColor: color.hex }}
                                  title={`Used ${color.frequency.toFixed(0)}% of the time`}
                                />
                                <p className="text-xs text-center text-muted-foreground">{color.frequency.toFixed(0)}%</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
                        <BarChart3 className="w-8 h-8 text-muted-foreground" />
                      </div>
                      <p className="text-muted-foreground">
                        No color analytics available yet. Generate content to see insights.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="border-0 shadow-lg">
                <CardHeader className="space-y-3">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-950 dark:to-pink-950 flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-purple-600" />
                    </div>
                    <CardTitle>Style Analysis</CardTitle>
                  </div>
                  <CardDescription>Visual style consistency across content</CardDescription>
                </CardHeader>
                <CardContent>
                  {insights?.style_insights?.detected_styles ? (
                    <div className="space-y-4">
                      {Object.entries(insights.style_insights.detected_styles).map(([style, count]) => (
                        <div key={style} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <span className="text-sm font-medium capitalize">{style}</span>
                            <span className="text-sm text-muted-foreground">{String(count)}x</span>
                          </div>
                          <Progress value={(count as number) * 10} className="h-2" />
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="w-16 h-16 rounded-full bg-muted/50 flex items-center justify-center mx-auto mb-4">
                        <Eye className="w-8 h-8 text-muted-foreground" />
                      </div>
                      <p className="text-muted-foreground">
                        No style analytics available yet. Generate content to see insights.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-8">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-2xl font-bold">Campaigns</h2>
              <p className="text-muted-foreground">Create and manage your brand's campaigns</p>
            </div>
            <Button onClick={() => setCampaignDialogOpen(true)}>
              + New Campaign
            </Button>
          </div>
          <Dialog open={campaignDialogOpen} onOpenChange={setCampaignDialogOpen}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Create Campaign</DialogTitle>
                <DialogDescription>Define a new campaign for your brand</DialogDescription>
              </DialogHeader>
              <div className="space-y-3">
                <Input placeholder="Name" value={newCampaign.name} onChange={e => setNewCampaign({ ...newCampaign, name: e.target.value })} />
                <Input placeholder="Description" value={newCampaign.description} onChange={e => setNewCampaign({ ...newCampaign, description: e.target.value })} />
                <Input placeholder="Type (e.g. product_launch)" value={newCampaign.campaign_type} onChange={e => setNewCampaign({ ...newCampaign, campaign_type: e.target.value })} />
                <Input placeholder="Start Date (YYYY-MM-DD)" value={newCampaign.start_date} onChange={e => setNewCampaign({ ...newCampaign, start_date: e.target.value })} />
                <Input placeholder="End Date (YYYY-MM-DD)" value={newCampaign.end_date} onChange={e => setNewCampaign({ ...newCampaign, end_date: e.target.value })} />
                <Input placeholder="Target Platforms (comma separated)" value={newCampaign.target_platforms} onChange={e => setNewCampaign({ ...newCampaign, target_platforms: e.target.value })} />
                <div className="flex gap-2">
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    placeholder="Engagement Rate (%)"
                    value={metrics.engagement_rate}
                    onChange={e => setMetrics({ ...metrics, engagement_rate: e.target.value })}
                  />
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    placeholder="Conversion Rate (%)"
                    value={metrics.conversion_rate}
                    onChange={e => setMetrics({ ...metrics, conversion_rate: e.target.value })}
                  />
                  <Input
                    type="number"
                    min="0"
                    step="any"
                    placeholder="Reach"
                    value={metrics.reach}
                    onChange={e => setMetrics({ ...metrics, reach: e.target.value })}
                  />
                </div>
                <Button onClick={handleCreateCampaign} disabled={creatingCampaign} className="w-full">
                  {creatingCampaign ? "Creating..." : "Create"}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
          <div className="space-y-4">
            {campaigns.length === 0 ? (
              <Card className="border-2 border-dashed border-muted-foreground/25 bg-muted/5">
                <CardContent className="flex flex-col items-center justify-center py-16 text-center space-y-6">
                  <Target className="w-10 h-10 text-violet-600" />
                  <div className="space-y-2">
                    <h3 className="text-xl font-semibold">No campaigns yet</h3>
                    <p className="text-muted-foreground max-w-md">
                      Create a campaign to track and optimize your brand's marketing efforts.
                    </p>
                  </div>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                {campaigns.map((campaign) => (
                  <Card key={campaign.id} className="border-0 shadow-lg">
                    <CardHeader>
                      <CardTitle>{campaign.name}</CardTitle>
                      <CardDescription>{campaign.description}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <div><b>Type:</b> {campaign.campaign_type}</div>
                      <div><b>Start:</b> {campaign.start_date}</div>
                      <div><b>End:</b> {campaign.end_date}</div>
                      <div><b>Platforms:</b> {Array.isArray(campaign.target_platforms) ? campaign.target_platforms.join(", ") : campaign.target_platforms}</div>
                      <div><b>Metrics:</b> {campaign.target_metrics ? JSON.stringify(campaign.target_metrics) : "-"}</div>
                      <Button
                        className="mt-2"
                        onClick={() => window.open(`/dashboard/generate?brand=${brandId}&campaign=${campaign.id}`, "_blank")}
                        variant="outline"
                        size="sm"
                      >
                        Generate Content
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}