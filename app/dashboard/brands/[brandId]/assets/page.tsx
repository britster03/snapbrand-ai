"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Upload, Eye, Download, Trash2, Filter, Search, Grid, List } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { useToast } from "@/components/ui/use-toast"
import { AuthUtils } from "@/lib/auth-utils"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

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

interface BrandProfile {
  id: number
  name: string
  industry: string
}

const ASSET_TYPES = [
  { value: "logo", label: "Logo" },
  { value: "product-image", label: "Product Image" },
  { value: "marketing-material", label: "Marketing Material" },
  { value: "social-media", label: "Social Media" },
  { value: "website-asset", label: "Website Asset" },
  { value: "print-material", label: "Print Material" },
  { value: "other", label: "Other" }
]

export default function BrandAssetsPage() {
  const params = useParams()
  const router = useRouter()
  const brandId = params.brandId as string
  const { toast } = useToast()

  const [brand, setBrand] = useState<BrandProfile | null>(null)
  const [assets, setAssets] = useState<BrandAsset[]>([])
  const [filteredAssets, setFilteredAssets] = useState<BrandAsset[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  
  // Filters
  const [searchTerm, setSearchTerm] = useState("")
  const [assetTypeFilter, setAssetTypeFilter] = useState("all")
  const [analysisFilter, setAnalysisFilter] = useState("all")
  
  // Upload form
  const [uploadForm, setUploadForm] = useState({
    asset_type: "",
    asset_name: "",
    file: null as File | null
  })

  useEffect(() => {
    fetchBrandData()
  }, [brandId])

  useEffect(() => {
    filterAssets()
  }, [assets, searchTerm, assetTypeFilter, analysisFilter])

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

  const filterAssets = () => {
    let filtered = assets

    if (searchTerm) {
      filtered = filtered.filter(asset => 
        asset.asset_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        asset.asset_type.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (assetTypeFilter && assetTypeFilter !== "all") {
      filtered = filtered.filter(asset => asset.asset_type === assetTypeFilter)
    }

    if (analysisFilter && analysisFilter !== "all") {
      if (analysisFilter === "analyzed") {
        filtered = filtered.filter(asset => asset.analysis_completed)
      } else if (analysisFilter === "pending") {
        filtered = filtered.filter(asset => !asset.analysis_completed)
      }
    }

    setFilteredAssets(filtered)
  }

  const handleAssetUpload = async (event: React.FormEvent) => {
    event.preventDefault()
    
    if (!uploadForm.file || !uploadForm.asset_type || !uploadForm.asset_name) {
      toast({
        title: "Validation Error",
        description: "Please fill in all required fields",
        variant: "destructive",
      })
      return
    }

    setUploading(true)
    const formData = new FormData()
    formData.append("file", uploadForm.file)
    formData.append("asset_type", uploadForm.asset_type)
    formData.append("asset_name", uploadForm.asset_name)

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
          title: "Success",
          description: "Asset uploaded successfully",
        })
        setUploadDialogOpen(false)
        setUploadForm({ asset_type: "", asset_name: "", file: null })
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

  const downloadAsset = (asset: BrandAsset) => {
    const link = document.createElement("a")
    link.href = asset.asset_url
    link.download = asset.asset_name
    link.target = "_blank"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown"
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + " " + sizes[i]
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString()
  }

  if (loading || !brand) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <Button
          variant="ghost"
          onClick={() => router.push(`/dashboard/brands/${brandId}`)}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Back to Brand Profile
        </Button>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">{brand.name} - Assets</h1>
            <p className="text-muted-foreground mt-2">Manage your brand assets and analyze their properties</p>
          </div>
          <Dialog open={uploadDialogOpen} onOpenChange={setUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Upload className="mr-2 h-4 w-4" />
                Upload Asset
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Upload Brand Asset</DialogTitle>
                <DialogDescription>
                  Upload logos, images, or other brand assets for analysis
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleAssetUpload} className="space-y-4">
                <div>
                  <Label htmlFor="asset-name">Asset Name *</Label>
                  <Input
                    id="asset-name"
                    value={uploadForm.asset_name}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, asset_name: e.target.value }))}
                    placeholder="Enter asset name"
                    required
                  />
                </div>
                
                <div>
                  <Label htmlFor="asset-type">Asset Type *</Label>
                  <Select 
                    value={uploadForm.asset_type} 
                    onValueChange={(value) => setUploadForm(prev => ({ ...prev, asset_type: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select asset type" />
                    </SelectTrigger>
                    <SelectContent>
                      {ASSET_TYPES.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                
                <div>
                  <Label htmlFor="asset-file">Select File *</Label>
                  <Input
                    id="asset-file"
                    type="file"
                    accept="image/*"
                    onChange={(e) => setUploadForm(prev => ({ ...prev, file: e.target.files?.[0] || null }))}
                    required
                  />
                </div>
                
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setUploadDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={uploading}>
                    {uploading ? "Uploading..." : "Upload"}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters and Search */}
      <Card className="mb-6">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={assetTypeFilter} onValueChange={setAssetTypeFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {ASSET_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={analysisFilter} onValueChange={setAnalysisFilter}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by analysis" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Assets</SelectItem>
                <SelectItem value="analyzed">Analyzed</SelectItem>
                <SelectItem value="pending">Pending Analysis</SelectItem>
              </SelectContent>
            </Select>
            
            <div className="flex rounded-md border">
              <Button
                variant={viewMode === "grid" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("grid")}
              >
                <Grid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === "list" ? "default" : "ghost"}
                size="sm"
                onClick={() => setViewMode("list")}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Assets Display */}
      {filteredAssets.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <h3 className="text-lg font-semibold mb-2">
              {assets.length === 0 ? "No assets uploaded yet" : "No assets match your filters"}
            </h3>
            <p className="text-muted-foreground mb-4">
              {assets.length === 0 
                ? "Upload your logo and brand assets to extract colors and style attributes"
                : "Try adjusting your search or filter criteria"
              }
            </p>
            {assets.length === 0 && (
              <Button onClick={() => setUploadDialogOpen(true)}>
                <Upload className="mr-2 h-4 w-4" />
                Upload First Asset
              </Button>
            )}
          </CardContent>
        </Card>
      ) : viewMode === "grid" ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filteredAssets.map((asset) => (
            <Card key={asset.id} className="overflow-hidden">
              <div className="aspect-square relative">
                <img
                  src={asset.asset_url}
                  alt={asset.asset_name}
                  className="w-full h-full object-cover"
                />
                {asset.analysis_completed && (
                  <Badge className="absolute top-2 right-2" variant="secondary">
                    Analyzed
                  </Badge>
                )}
              </div>
              <CardContent className="p-4">
                <h4 className="font-semibold truncate">{asset.asset_name}</h4>
                <p className="text-sm text-muted-foreground capitalize">{asset.asset_type.replace("-", " ")}</p>
                
                {asset.dominant_colors && asset.dominant_colors.length > 0 && (
                  <div className="mt-3">
                    <span className="text-xs text-muted-foreground">Colors</span>
                    <div className="flex space-x-1 mt-1">
                      {asset.dominant_colors.slice(0, 5).map((color, index) => (
                        <div
                          key={index}
                          className="w-6 h-6 rounded border"
                          style={{ backgroundColor: color.hex }}
                          title={`${color.hex} (${color.percentage}%)`}
                        />
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="flex justify-between items-center mt-4">
                  <div className="flex space-x-1">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => window.open(asset.asset_url, "_blank")}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => downloadAsset(asset)}
                    >
                      <Download className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => deleteAsset(asset.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="p-0">
            <div className="divide-y">
              {filteredAssets.map((asset) => (
                <div key={asset.id} className="p-4 flex items-center space-x-4">
                  <img
                    src={asset.asset_url}
                    alt={asset.asset_name}
                    className="w-16 h-16 rounded object-cover"
                  />
                  <div className="flex-1">
                    <h4 className="font-semibold">{asset.asset_name}</h4>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                      <span className="capitalize">{asset.asset_type.replace("-", " ")}</span>
                      <span>{formatFileSize(asset.file_size)}</span>
                      <span>{formatDate(asset.created_at)}</span>
                      {asset.dimensions && (
                        <span>{asset.dimensions.width}×{asset.dimensions.height}</span>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    {asset.analysis_completed && (
                      <Badge variant="secondary">Analyzed</Badge>
                    )}
                    <div className="flex space-x-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(asset.asset_url, "_blank")}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => downloadAsset(asset)}
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => deleteAsset(asset.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}