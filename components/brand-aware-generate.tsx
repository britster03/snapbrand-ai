"use client"

import { useState, useEffect } from "react"
import { Palette, Sparkles, AlertCircle } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { AuthUtils } from "@/lib/auth-utils"
import { useRouter } from "next/navigation"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface BrandProfile {
  id: number
  name: string
  industry: string
  visual_style?: string
  primary_colors: string[]
  brand_keywords: string[]
}

interface BrandAwareGenerateProps {
  onGenerate: (params: any) => void
  prompt: string
  setPrompt: (prompt: string) => void
  setEnhancedPrompt?: (enhanced: string) => void
  setSelectedBrandId?: (id: string) => void
  setSelectedBrand?: (brand: BrandProfile | null) => void
}

export function BrandAwareGenerate({ onGenerate, prompt, setPrompt, setEnhancedPrompt, setSelectedBrandId, setSelectedBrand }: BrandAwareGenerateProps) {
  const [brands, setBrands] = useState<BrandProfile[]>([])
  const [selectedBrandId, setSelectedBrandIdState] = useState("")
  const [selectedBrand, setSelectedBrandState] = useState<BrandProfile | null>(null)
  const [useBrandGuidelines, setUseBrandGuidelines] = useState(true)
  const [brandConsistencyCheck, setBrandConsistencyCheck] = useState(true)
  const [loading, setLoading] = useState(false)
  const [enhancedPrompt, setEnhancedPromptState] = useState("")
  const { toast } = useToast()
  const router = useRouter()

  useEffect(() => {
    fetchBrands()
  }, [])

  useEffect(() => {
    if (selectedBrandId && selectedBrandId !== "none") {
      const brand = brands.find(b => b.id.toString() === selectedBrandId)
      setSelectedBrandState(brand || null)
      if (brand && prompt) {
        enhancePromptWithBrand(prompt, brand)
      }
    } else {
      setSelectedBrandState(null)
      setEnhancedPromptState("")
    }
  }, [selectedBrandId, prompt])

  // Whenever selectedBrandId changes, call setSelectedBrandId if provided
  useEffect(() => {
    if (setSelectedBrandId) setSelectedBrandId(selectedBrandId)
  }, [selectedBrandId, setSelectedBrandId])

  // Whenever selectedBrand changes, call setSelectedBrand if provided
  useEffect(() => {
    if (setSelectedBrand) setSelectedBrand(selectedBrand)
  }, [selectedBrand, setSelectedBrand])

  // Whenever enhancedPrompt changes, call setEnhancedPrompt if provided
  useEffect(() => {
    if (setEnhancedPrompt) setEnhancedPrompt(enhancedPrompt)
  }, [enhancedPrompt, setEnhancedPrompt])

  const fetchBrands = async () => {
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
      
      const response = await fetch(`${API_URL}/brands/profiles`, {
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
        setBrands(data)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch brand profiles",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching brands:", error)
      toast({
        title: "Error",
        description: "Failed to connect to server",
        variant: "destructive",
      })
    }
  }

  const enhancePromptWithBrand = async (basePrompt: string, brand: BrandProfile) => {
    if (!useBrandGuidelines) {
      setEnhancedPromptState("")
      return
    }

    setLoading(true)
    try {
      // In a real implementation, this would call the brand consistency validator
      // For now, we'll create a simple enhanced prompt
      const brandElements = []
      
      if (brand.visual_style) {
        brandElements.push(`${brand.visual_style} style`)
      }
      
      if (brand.primary_colors && brand.primary_colors.length > 0) {
        brandElements.push(`using ${brand.primary_colors.slice(0, 3).join(", ")} color palette`)
      }
      
      if (brand.brand_keywords && brand.brand_keywords.length > 0) {
        brandElements.push(`embodying ${brand.brand_keywords.slice(0, 3).join(", ")}`)
      }
      
      const industryModifiers = {
        "e-commerce": "product-focused, commercial photography style",
        "saas": "modern tech aesthetic, clean UI",
        "healthcare": "professional, trust-inspiring",
        "finance": "corporate professional, established",
      }
      
      const industryModifier = industryModifiers[brand.industry as keyof typeof industryModifiers]
      if (industryModifier) {
        brandElements.push(industryModifier)
      }
      
      const enhanced = `${basePrompt}, ${brandElements.join(", ")}`
      setEnhancedPromptState(enhanced)
    } catch (error) {
      console.error("Error enhancing prompt:", error)
      toast({
        title: "Error",
        description: "Failed to enhance prompt with brand guidelines",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = () => {
    const params: any = {
      prompt: enhancedPrompt || prompt,
      brand_profile_id: selectedBrandId ? parseInt(selectedBrandId) : undefined,
    }

    if (selectedBrand) {
      params.brand_metadata = {
        name: selectedBrand.name,
        industry: selectedBrand.industry,
        visual_style: selectedBrand.visual_style,
        primary_colors: selectedBrand.primary_colors,
      }
    }

    onGenerate(params)
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <Palette className="h-5 w-5" />
          <span>Brand Intelligence</span>
        </CardTitle>
        <CardDescription>
          Apply brand guidelines to ensure consistent image generation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <Label htmlFor="brand-select">Brand Profile</Label>
          <Select value={selectedBrandId} onValueChange={setSelectedBrandIdState}>
            <SelectTrigger id="brand-select">
              <SelectValue placeholder="Select a brand profile (optional)" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">No brand profile</SelectItem>
              {brands.map((brand) => (
                <SelectItem key={brand.id} value={brand.id.toString()}>
                  <div className="flex items-center space-x-2">
                    <span>{brand.name}</span>
                    <Badge variant="outline" className="text-xs">
                      {brand.industry}
                    </Badge>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {selectedBrand && (
          <>
            <div className="space-y-3 p-4 bg-muted rounded-lg">
              <div className="flex items-center justify-between">
                <Label htmlFor="use-guidelines">Apply Brand Guidelines</Label>
                <Switch
                  id="use-guidelines"
                  checked={useBrandGuidelines}
                  onCheckedChange={setUseBrandGuidelines}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="consistency-check">Brand Consistency Check</Label>
                <Switch
                  id="consistency-check"
                  checked={brandConsistencyCheck}
                  onCheckedChange={setBrandConsistencyCheck}
                />
              </div>
            </div>

            {selectedBrand.primary_colors && selectedBrand.primary_colors.length > 0 && (
              <div>
                <Label>Brand Colors</Label>
                <div className="flex space-x-2 mt-2">
                  {selectedBrand.primary_colors.map((color, index) => (
                    <div
                      key={index}
                      className="w-8 h-8 rounded border"
                      style={{ backgroundColor: color }}
                      title={color}
                    />
                  ))}
                </div>
              </div>
            )}

            {useBrandGuidelines && enhancedPrompt && (
              <Alert>
                <Sparkles className="h-4 w-4" />
                <AlertDescription>
                  <strong>Enhanced with brand guidelines:</strong>
                  <div className="mt-2 p-2 bg-background rounded text-sm">
                    {enhancedPrompt}
                  </div>
                </AlertDescription>
              </Alert>
            )}

            <Button
              className="w-full"
              onClick={() => window.open(`/dashboard/brands/${selectedBrand.id}`, "_blank")}
              variant="outline"
            >
              View Brand Profile
            </Button>
          </>
        )}

        {brands.length === 0 && (
          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              No brand profiles found. Create a brand profile to ensure consistent image generation.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}