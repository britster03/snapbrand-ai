"use client"

import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, Save, Trash2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
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
}

const INDUSTRIES = [
  { value: "technology", label: "Technology" },
  { value: "healthcare", label: "Healthcare" },
  { value: "finance", label: "Finance" },
  { value: "e-commerce", label: "E-commerce" },
  { value: "education", label: "Education" },
  { value: "entertainment", label: "Entertainment" },
  { value: "food-beverage", label: "Food & Beverage" },
  { value: "fashion", label: "Fashion" },
  { value: "automotive", label: "Automotive" },
  { value: "real-estate", label: "Real Estate" },
  { value: "travel", label: "Travel" },
  { value: "other", label: "Other" }
]

const VISUAL_STYLES = [
  { value: "modern", label: "Modern" },
  { value: "minimalist", label: "Minimalist" },
  { value: "vintage", label: "Vintage" },
  { value: "playful", label: "Playful" },
  { value: "professional", label: "Professional" },
  { value: "artistic", label: "Artistic" },
  { value: "bold", label: "Bold" },
  { value: "elegant", label: "Elegant" }
]

export default function BrandEditPage() {
  const params = useParams()
  const router = useRouter()
  const brandId = params.brandId as string
  const { toast } = useToast()

  const [brand, setBrand] = useState<BrandProfile | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  
  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    industry: "",
    visual_style: "",
    primary_colors: [] as string[],
    secondary_colors: [] as string[],
    brand_keywords: [] as string[]
  })
  
  const [newPrimaryColor, setNewPrimaryColor] = useState("#000000")
  const [newSecondaryColor, setNewSecondaryColor] = useState("#000000")
  const [newKeyword, setNewKeyword] = useState("")

  useEffect(() => {
    fetchBrand()
  }, [brandId])

  const fetchBrand = async () => {
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
      
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}`, {
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
        const data = await response.json()
        setBrand(data)
        setFormData({
          name: data.name || "",
          description: data.description || "",
          industry: data.industry || "",
          visual_style: data.visual_style || "",
          primary_colors: data.primary_colors || [],
          secondary_colors: data.secondary_colors || [],
          brand_keywords: data.brand_keywords || []
        })
      } else {
        toast({
          title: "Error",
          description: "Failed to load brand data",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching brand:", error)
      toast({
        title: "Error",
        description: "Failed to load brand data",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast({
        title: "Validation Error",
        description: "Brand name is required",
        variant: "destructive",
      })
      return
    }

    setSaving(true)
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
      
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}`, {
        method: "PUT",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      })

      if (response.status === 401) {
        AuthUtils.clearAuth()
        router.push("/login")
        return
      }

      if (response.ok) {
        toast({
          title: "Success",
          description: "Brand profile updated successfully",
        })
        router.push(`/dashboard/brands/${brandId}`)
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to update brand profile",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error updating brand:", error)
      toast({
        title: "Error",
        description: "Failed to update brand profile",
        variant: "destructive",
      })
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this brand profile? This action cannot be undone.")) {
      return
    }

    setDeleting(true)
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
      
      const response = await fetch(`${API_URL}/brands/profiles/${brandId}`, {
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
          description: "Brand profile deleted successfully",
        })
        router.push("/dashboard/brands")
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || "Failed to delete brand profile",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error deleting brand:", error)
      toast({
        title: "Error",
        description: "Failed to delete brand profile",
        variant: "destructive",
      })
    } finally {
      setDeleting(false)
    }
  }

  const addPrimaryColor = () => {
    if (newPrimaryColor && !formData.primary_colors.includes(newPrimaryColor)) {
      setFormData(prev => ({
        ...prev,
        primary_colors: [...prev.primary_colors, newPrimaryColor]
      }))
      setNewPrimaryColor("#000000")
    }
  }

  const removePrimaryColor = (color: string) => {
    setFormData(prev => ({
      ...prev,
      primary_colors: prev.primary_colors.filter(c => c !== color)
    }))
  }

  const addSecondaryColor = () => {
    if (newSecondaryColor && !formData.secondary_colors.includes(newSecondaryColor)) {
      setFormData(prev => ({
        ...prev,
        secondary_colors: [...prev.secondary_colors, newSecondaryColor]
      }))
      setNewSecondaryColor("#000000")
    }
  }

  const removeSecondaryColor = (color: string) => {
    setFormData(prev => ({
      ...prev,
      secondary_colors: prev.secondary_colors.filter(c => c !== color)
    }))
  }

  const addKeyword = () => {
    if (newKeyword.trim() && !formData.brand_keywords.includes(newKeyword.trim())) {
      setFormData(prev => ({
        ...prev,
        brand_keywords: [...prev.brand_keywords, newKeyword.trim()]
      }))
      setNewKeyword("")
    }
  }

  const removeKeyword = (keyword: string) => {
    setFormData(prev => ({
      ...prev,
      brand_keywords: prev.brand_keywords.filter(k => k !== keyword)
    }))
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
            <h1 className="text-3xl font-bold">Edit Brand Profile</h1>
            <p className="text-muted-foreground mt-2">Update your brand information and guidelines</p>
          </div>
          <div className="flex space-x-2">
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleting}
            >
              <Trash2 className="mr-2 h-4 w-4" />
              {deleting ? "Deleting..." : "Delete"}
            </Button>
            <Button onClick={handleSave} disabled={saving}>
              <Save className="mr-2 h-4 w-4" />
              {saving ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Basic Information</CardTitle>
            <CardDescription>Update your brand's basic details</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Brand Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                placeholder="Enter brand name"
              />
            </div>
            
            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe your brand..."
                rows={3}
              />
            </div>
            
            <div>
              <Label htmlFor="industry">Industry</Label>
              <Select value={formData.industry} onValueChange={(value) => setFormData(prev => ({ ...prev, industry: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select industry" />
                </SelectTrigger>
                <SelectContent>
                  {INDUSTRIES.map((industry) => (
                    <SelectItem key={industry.value} value={industry.value}>
                      {industry.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <Label htmlFor="visual-style">Visual Style</Label>
              <Select value={formData.visual_style} onValueChange={(value) => setFormData(prev => ({ ...prev, visual_style: value }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Select visual style" />
                </SelectTrigger>
                <SelectContent>
                  {VISUAL_STYLES.map((style) => (
                    <SelectItem key={style.value} value={style.value}>
                      {style.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Brand Colors</CardTitle>
            <CardDescription>Define your brand's color palette</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Primary Colors</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.primary_colors.map((color, index) => (
                  <div key={index} className="flex items-center space-x-1">
                    <div
                      className="w-8 h-8 rounded border cursor-pointer"
                      style={{ backgroundColor: color }}
                      title={color}
                      onClick={() => removePrimaryColor(color)}
                    />
                    <span className="text-sm">{color}</span>
                  </div>
                ))}
              </div>
              <div className="flex items-center space-x-2 mt-2">
                <Input
                  type="color"
                  value={newPrimaryColor}
                  onChange={(e) => setNewPrimaryColor(e.target.value)}
                  className="w-16"
                />
                <Input
                  value={newPrimaryColor}
                  onChange={(e) => setNewPrimaryColor(e.target.value)}
                  placeholder="#000000"
                  className="flex-1"
                />
                <Button onClick={addPrimaryColor} size="sm">Add</Button>
              </div>
            </div>
            
            <div>
              <Label>Secondary Colors</Label>
              <div className="flex flex-wrap gap-2 mt-2">
                {formData.secondary_colors.map((color, index) => (
                  <div key={index} className="flex items-center space-x-1">
                    <div
                      className="w-8 h-8 rounded border cursor-pointer"
                      style={{ backgroundColor: color }}
                      title={color}
                      onClick={() => removeSecondaryColor(color)}
                    />
                    <span className="text-sm">{color}</span>
                  </div>
                ))}
              </div>
              <div className="flex items-center space-x-2 mt-2">
                <Input
                  type="color"
                  value={newSecondaryColor}
                  onChange={(e) => setNewSecondaryColor(e.target.value)}
                  className="w-16"
                />
                <Input
                  value={newSecondaryColor}
                  onChange={(e) => setNewSecondaryColor(e.target.value)}
                  placeholder="#000000"
                  className="flex-1"
                />
                <Button onClick={addSecondaryColor} size="sm">Add</Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Brand Keywords</CardTitle>
            <CardDescription>Keywords that describe your brand values and personality</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {formData.brand_keywords.map((keyword, index) => (
                <Badge
                  key={index}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => removeKeyword(keyword)}
                >
                  {keyword} ×
                </Badge>
              ))}
            </div>
            <div className="flex items-center space-x-2">
              <Input
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                placeholder="Add a keyword..."
                onKeyPress={(e) => e.key === "Enter" && addKeyword()}
              />
              <Button onClick={addKeyword} size="sm">Add</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}