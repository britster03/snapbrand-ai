"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { 
  Sparkles, 
  Download, 
  Copy, 
  RefreshCw, 
  Image as ImageIcon,
  Palette,
  Settings,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  Info,
  HelpCircle,
  ChevronDown,
  ChevronUp,
  Star,
  Target
} from "lucide-react"
import { toast } from "sonner"
import Image from "next/image"
import Link from "next/link"
import { ProtectedRoute } from "@/components/protected-route"
import { BrandAwareGenerate } from "@/components/brand-aware-generate"
import { useSearchParams } from "next/navigation"

import { 
  apiClient, 
  type GenerateRequest, 
  type GeneratedImage, 
  type Template 
} from "@/lib/api"
import { AuthUtils } from "@/lib/auth-utils"

// Detailed option explanations
const qualityOptions = {
  standard: {
    name: "Standard",
    description: "Good quality for basic use cases",
    details: "512px minimum resolution, basic enhancement, suitable for drafts and quick previews",
    icon: "📱",
    cost: "Standard cost"
  },
  high: {
    name: "High Quality",
    description: "Enhanced quality for professional needs",
    details: "768px minimum resolution, improved sharpness and detail, great for most professional uses",
    icon: "🖥️",
    cost: "Standard cost"
  },
  ultra: {
    name: "Ultra High",
    description: "Premium quality for important content",
    details: "1024px minimum resolution, superior detail and clarity, perfect for marketing materials",
    icon: "🎯",
    cost: "Standard cost"
  },
  professional: {
    name: "Professional Grade",
    description: "Industry-grade for critical applications",
    details: "1024px+ resolution, maximum quality with professional validation, ideal for commercial use",
    icon: "⭐",
    cost: "Standard cost"
  }
}

const styleCategories = {
  photorealistic: {
    name: "Photorealistic",
    description: "Realistic, natural-looking images",
    details: "Creates images that look like real photographs with natural lighting and authentic details",
    icon: "📸",
    examples: ["Product photos", "Portrait shots", "Lifestyle images"]
  },
  artistic: {
    name: "Artistic",
    description: "Creative and expressive style",
    details: "Stylized images with creative flair, perfect for artistic projects and unique visuals",
    icon: "🎨",
    examples: ["Digital art", "Creative concepts", "Artistic portraits"]
  },
  technical: {
    name: "Technical",
    description: "Clean, precise documentation style",
    details: "Clear, precise images ideal for technical documentation, diagrams, and instructional content",
    icon: "📐",
    examples: ["Technical diagrams", "Product manuals", "Instructional graphics"]
  },
  marketing: {
    name: "Marketing",
    description: "Commercial and brand-focused",
    details: "Optimized for marketing materials with appealing composition and brand alignment",
    icon: "📈",
    examples: ["Social media", "Advertisements", "Brand campaigns"]
  },
  product: {
    name: "Product Photography",
    description: "Professional product showcase",
    details: "Studio-quality product images with clean backgrounds and optimal lighting for e-commerce",
    icon: "📦",
    examples: ["E-commerce", "Catalogs", "Product showcases"]
  }
}

const compositionRules = {
  none: {
    name: "Auto",
    description: "AI chooses the best composition",
    details: "Let the AI automatically select the most appropriate composition for your image",
    icon: "🤖"
  },
  rule_of_thirds: {
    name: "Rule of Thirds",
    description: "Classic photography composition",
    details: "Divides image into thirds, placing subjects along lines or intersections for visual balance",
    icon: "⚏"
  },
  center_composition: {
    name: "Center Composition",
    description: "Subject centered in frame",
    details: "Places the main subject in the center for strong, focused impact - great for portraits and products",
    icon: "⊙"
  },
  leading_lines: {
    name: "Leading Lines",
    description: "Lines that guide the eye",
    details: "Uses lines to draw attention to the main subject, creating depth and visual flow",
    icon: "↗"
  },
  symmetry: {
    name: "Symmetry",
    description: "Balanced, mirrored composition",
    details: "Creates harmonious balance through symmetrical elements, ideal for architecture and formal subjects",
    icon: "⚖"
  },
  golden_ratio: {
    name: "Golden Ratio",
    description: "Mathematically perfect composition",
    details: "Uses the golden ratio (1.618:1) for naturally pleasing proportions, often used in fine art",
    icon: "φ"
  }
}

const lightingPresets = {
  professional: {
    name: "Professional",
    description: "Balanced professional lighting",
    details: "Three-point lighting setup with balanced shadows and highlights, perfect for most professional needs",
    icon: "💡"
  },
  studio: {
    name: "Studio",
    description: "Controlled studio environment",
    details: "Soft, even lighting with minimal shadows, ideal for product photography and portraits",
    icon: "🏢"
  },
  natural: {
    name: "Natural",
    description: "Soft daylight appearance",
    details: "Mimics natural daylight with realistic shadows, great for lifestyle and outdoor scenes",
    icon: "☀️"
  },
  dramatic: {
    name: "Dramatic",
    description: "High contrast, cinematic look",
    details: "Strong contrasts and bold shadows for impactful, cinematic images",
    icon: "🎬"
  },
  soft: {
    name: "Soft",
    description: "Gentle, diffused lighting",
    details: "Soft, diffused light with minimal harsh shadows, perfect for gentle, welcoming images",
    icon: "🕯️"
  },
  golden_hour: {
    name: "Golden Hour",
    description: "Warm, glowing light",
    details: "Warm, golden tones that mimic the magical hour before sunset, adds warmth and appeal",
    icon: "🌅"
  }
}

// Brand style presets based on the brand assets
const brandStyles = {
  default: {
    name: "Default",
    description: "No specific brand style",
    colors: [],
    style_keywords: []
  },
  professional: {
    name: "Professional",
    description: "Clean, corporate, and professional aesthetic",
    colors: ["#3B82F6", "#6B7280", "#F8FAFC"],
    style_keywords: ["professional", "clean", "corporate", "minimal"]
  },
  vibrant: {
    name: "Vibrant",
    description: "Bold colors and energetic design",
    colors: ["#8B5CF6", "#10B981", "#F59E0B"],
    style_keywords: ["vibrant", "bold", "energetic", "colorful"]
  },
  minimal: {
    name: "Minimal",
    description: "Simple, clean, and minimalist approach",
    colors: ["#FFFFFF", "#F3F4F6", "#374151"],
    style_keywords: ["minimal", "simple", "clean", "modern"]
  },
  luxury: {
    name: "Luxury",
    description: "Premium, elegant, and sophisticated",
    colors: ["#1F2937", "#D4AF37", "#FFFFFF"],
    style_keywords: ["luxury", "premium", "elegant", "sophisticated"]
  }
}

// Helper component for option explanations
const OptionExplanation = ({ 
  option, 
  children 
}: { 
  option: any, 
  children: React.ReactNode 
}) => (
  <TooltipProvider>
    <Tooltip>
      <TooltipTrigger asChild>
        {children}
      </TooltipTrigger>
      <TooltipContent side="right" className="max-w-xs">
        <div className="space-y-2">
          <div className="flex items-center space-x-2">
            <span className="text-lg">{option.icon}</span>
            <span className="font-medium">{option.name}</span>
          </div>
          <p className="text-sm text-gray-600">{option.details}</p>
          {option.examples && (
            <div className="text-xs text-gray-500">
              <span className="font-medium">Best for:</span> {option.examples.join(", ")}
            </div>
          )}
        </div>
      </TooltipContent>
    </Tooltip>
  </TooltipProvider>
)

export default function GeneratePage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState("all")
  
  const [prompt, setPrompt] = useState("")
  const [negativePrompt, setNegativePrompt] = useState("")
  const [numImages, setNumImages] = useState(1)
  const [size, setSize] = useState("1024x1024")
  const [guidanceScale, setGuidanceScale] = useState(7.5)
  const [seed, setSeed] = useState<number | undefined>(undefined)
  const [selectedBrandStyle, setSelectedBrandStyle] = useState("default")
  const [applyBrandColors, setApplyBrandColors] = useState(false)
  
  // Professional quality controls
  const [imageQuality, setImageQuality] = useState("high")
  const [imageStyle, setImageStyle] = useState("photorealistic")
  const [compositionRule, setCompositionRule] = useState("none")
  const [lightingPreset, setLightingPreset] = useState("professional")
  
  // UI state for collapsible sections
  const [showQualityDetails, setShowQualityDetails] = useState(false)
  const [showTemplateDetails, setShowTemplateDetails] = useState(false)
  const [showBrandDetails, setShowBrandDetails] = useState(false)
  
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([])
  const [processingTime, setProcessingTime] = useState<number>(0)
  const [totalCost, setTotalCost] = useState<number>(0)

  const [enhancedPrompt, setEnhancedPrompt] = useState("")
  const [selectedBrandId, setSelectedBrandId] = useState<string>("")
  const [selectedBrand, setSelectedBrand] = useState<any>(null)

  const searchParams = useSearchParams()
  const campaignIdFromQuery = searchParams?.get("campaign")
  const [campaign, setCampaign] = useState<any>(null)

  // Load templates on component mount
  useEffect(() => {
    loadTemplates()
    loadCategories()
  }, [])

  // Fetch campaign details if campaignIdFromQuery is present
  useEffect(() => {
    const fetchCampaign = async () => {
      if (!campaignIdFromQuery) return
      try {
        const token = AuthUtils.getToken && AuthUtils.getToken()
        if (!token) return
        const headers = { Authorization: `Bearer ${token}` }
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/brands/profiles/${selectedBrandId}/campaigns`, { headers })
        if (response.ok) {
          const data = await response.json()
          const found = data.find((c: any) => String(c.id) === String(campaignIdFromQuery))
          if (found) setCampaign(found)
        }
      } catch (e) { /* ignore */ }
    }
    fetchCampaign()
  }, [campaignIdFromQuery, selectedBrandId])

  const loadTemplates = async () => {
    try {
      const templateList = await apiClient.getTemplates(selectedCategory === "all" ? undefined : selectedCategory)
      setTemplates(templateList)
    } catch (error) {
      console.error("Failed to load templates:", error)
      toast.error("Failed to load templates")
    }
  }

  const loadCategories = async () => {
    try {
      const categoryList = await apiClient.getTemplateCategories()
      setCategories(categoryList)
    } catch (error) {
      console.error("Failed to load categories:", error)
    }
  }

  const handleTemplateSelect = (templateId: string) => {
    if (templateId === "none") {
      setSelectedTemplate(null)
      return
    }
    
    const template = templates.find(t => t.id === templateId)
    if (template) {
      setSelectedTemplate(template)
      setSize(template.default_size)
      if (template.negative_prompt) {
        setNegativePrompt(template.negative_prompt)
      }
      
      // Apply template-specific professional settings if available
      const templateData = template as any
      if (templateData.quality) {
        setImageQuality(templateData.quality)
      }
      if (templateData.style) {
        setImageStyle(templateData.style)
      }
      if (templateData.composition) {
        setCompositionRule(templateData.composition)
      }
      if (templateData.lighting) {
        setLightingPreset(templateData.lighting)
      }
      
      toast.success(`Template "${template.name}" applied with optimized settings!`)
    }
  }

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setSelectedTemplate(null)
  }

  const buildBrandStylePrompt = (basePrompt: string) => {
    if (selectedBrandStyle === "default") return basePrompt
    
    const brandStyle = brandStyles[selectedBrandStyle as keyof typeof brandStyles]
    let enhancedPrompt = basePrompt
    
    // Add brand style keywords
    if (brandStyle.style_keywords.length > 0) {
      enhancedPrompt += `, ${brandStyle.style_keywords.join(", ")} style`
    }
    
    // Add color palette information if enabled
    if (applyBrandColors && brandStyle.colors.length > 0) {
      enhancedPrompt += `, using color palette: ${brandStyle.colors.join(", ")}`
    }
    
    return enhancedPrompt
  }

  const generateImages = async () => {
    if (!(enhancedPrompt || prompt).trim()) {
      toast.error("Please enter a prompt")
      return
    }

    setIsGenerating(true)
    setGeneratedImages([])
    setProcessingTime(0)
    setTotalCost(0)

    try {
      // Build brand style object
      const brandStyleData = selectedBrandStyle !== "default" ? {
        style_name: selectedBrandStyle,
        colors: applyBrandColors ? brandStyles[selectedBrandStyle as keyof typeof brandStyles].colors : [],
        keywords: brandStyles[selectedBrandStyle as keyof typeof brandStyles].style_keywords
      } : undefined

      const request: GenerateRequest = {
        prompt: (enhancedPrompt || prompt).trim(),
        negative_prompt: negativePrompt.trim() || undefined,
        num_images: numImages,
        size,
        guidance_scale: guidanceScale,
        seed: seed || undefined,
        template_id: selectedTemplate?.id,
        brand_style: selectedBrand ? {
          name: selectedBrand.name,
          industry: selectedBrand.industry,
          visual_style: selectedBrand.visual_style,
          primary_colors: selectedBrand.primary_colors,
        } : undefined,
        // Professional quality parameters (these will be processed by the backend)
        quality: imageQuality,
        style: imageStyle,
        composition: compositionRule !== "none" ? compositionRule : undefined,
        lighting: lightingPreset,
        // Add campaign_id if present
        ...(campaign ? { campaign_id: campaign.id } : {})
      }

      const startTime = Date.now()
      const response = await apiClient.generateImages(request)
      const endTime = Date.now()

      setGeneratedImages(response.images)
      setProcessingTime((endTime - startTime) / 1000)
      setTotalCost(response.total_cost || 0)

      toast.success(`Generated ${response.images.length} images successfully!`)
    } catch (error: any) {
      console.error("Generation failed:", error)
      toast.error(error.message || "Failed to generate images")
    } finally {
      setIsGenerating(false)
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

  const copyPrompt = (image: GeneratedImage) => {
    navigator.clipboard.writeText(image.prompt)
    toast.success("Prompt copied to clipboard!")
  }

  const generateRandomSeed = () => {
    setSeed(Math.floor(Math.random() * 1000000))
  }

  const resetForm = () => {
    setPrompt("")
    setNegativePrompt("")
    setNumImages(1)
    setSize("1024x1024")
    setGuidanceScale(7.5)
    setSeed(undefined)
    setSelectedTemplate(null)
    setGeneratedImages([])
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50" suppressHydrationWarning>
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
              <Badge variant="secondary" className="bg-green-100 text-green-700">
                Generate Images
              </Badge>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm" onClick={resetForm}>
                <RefreshCw className="w-4 h-4 mr-2" />
                Reset
              </Button>
              <Button asChild>
                <Link href="/dashboard/batch">
                  <Zap className="w-4 h-4 mr-2" />
                  Batch Generate
                </Link>
              </Button>
            </div>
          </div>
        </header>

        <div className="flex">
          {/* Sidebar */}
          <aside className="w-80 bg-white border-r min-h-screen p-6">
            <div className="space-y-6">
              {/* Template Selection */}
              <div>
                <Label className="text-sm font-medium">Template Category</Label>
                <Select value={selectedCategory} onValueChange={handleCategoryChange}>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="All categories" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All categories</SelectItem>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">Template</Label>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setShowTemplateDetails(!showTemplateDetails)}
                  >
                    <Info className="w-4 h-4" />
                  </Button>
                </div>
                <Select value={selectedTemplate?.id || "none"} onValueChange={handleTemplateSelect}>
                  <SelectTrigger className="mt-2">
                    <SelectValue placeholder="Choose a template (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="none">No Template</SelectItem>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id}>
                        <div className="flex items-center space-x-2">
                          <span>{template.category === 'product' ? '📦' : 
                                template.category === 'social' ? '📱' : 
                                template.category === 'web' ? '🌐' : 
                                template.category === 'email' ? '📧' : 
                                template.category === 'technical' ? '📐' : 
                                template.category === 'brand' ? '✨' : 
                                template.category === 'corporate' ? '🏢' : 
                                template.category === 'event' ? '🎉' : '📄'}</span>
                          <span>{template.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                {showTemplateDetails && (
                  <Card className="mt-2 border-blue-200 bg-blue-50">
                    <CardContent className="p-3">
                      <div className="text-xs space-y-1">
                        <div className="font-medium text-blue-800">What are templates?</div>
                        <div className="text-blue-700">
                          Templates are pre-configured settings that optimize your image generation for specific use cases. 
                          They automatically set the best quality, style, composition, and lighting for your intended purpose.
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>

              {selectedTemplate && (
                <Card className="border-green-200 bg-green-50">
                  <CardHeader className="pb-3">
                    <div className="flex items-center space-x-2">
                      <Star className="w-4 h-4 text-green-600" />
                      <CardTitle className="text-sm text-green-800">{selectedTemplate.name}</CardTitle>
                    </div>
                    <CardDescription className="text-xs text-green-700">
                      {selectedTemplate.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-2">
                      <div className="text-xs text-green-700">
                        <div><strong>Category:</strong> {selectedTemplate.category}</div>
                        <div><strong>Optimized Size:</strong> {selectedTemplate.default_size}</div>
                        {selectedTemplate.negative_prompt && (
                          <div><strong>Includes:</strong> Professional negative prompts</div>
                        )}
                      </div>
                      <div className="text-xs text-green-600 bg-green-100 p-2 rounded">
                        <strong>Template Benefits:</strong> This template automatically optimizes quality settings, 
                        composition rules, and lighting for {selectedTemplate.category} content.
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              <Separator />

              {/* Generation Settings */}
              <div className="space-y-4">
                <div>
                  <Label className="text-sm font-medium">Number of Images</Label>
                  <Select value={numImages.toString()} onValueChange={(value) => setNumImages(parseInt(value))}>
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((num) => (
                        <SelectItem key={num} value={num.toString()}>
                          {num}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-sm font-medium">Image Size</Label>
                  <Select value={size} onValueChange={setSize}>
                    <SelectTrigger className="mt-2">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="512x512">512x512</SelectItem>
                      <SelectItem value="768x768">768x768</SelectItem>
                      <SelectItem value="1024x1024">1024x1024</SelectItem>
                      <SelectItem value="1024x768">1024x768</SelectItem>
                      <SelectItem value="768x1024">768x1024</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label className="text-sm font-medium">
                    Guidance Scale: {guidanceScale}
                  </Label>
                  <Slider
                    value={[guidanceScale]}
                    onValueChange={([value]) => setGuidanceScale(value)}
                    max={20}
                    min={1}
                    step={0.5}
                    className="mt-2"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    Higher values = more adherence to prompt
                  </div>
                </div>

                <div>
                  <Label className="text-sm font-medium">Seed (Optional)</Label>
                  <div className="flex space-x-2 mt-2">
                    <Input
                      type="number"
                      value={seed || ""}
                      onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value) : undefined)}
                      placeholder="Random"
                    />
                    <Button variant="outline" size="sm" onClick={generateRandomSeed}>
                      <RefreshCw className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </div>

              <Separator />

              {/* Professional Quality Controls */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Settings className="w-4 h-4" />
                    <Label className="text-sm font-medium">Professional Quality</Label>
                  </div>
                  <Button 
                    variant="ghost" 
                    size="sm"
                    onClick={() => setShowQualityDetails(!showQualityDetails)}
                  >
                    {showQualityDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </Button>
                </div>
                
                {showQualityDetails && (
                  <Card className="border-purple-200 bg-purple-50">
                    <CardContent className="p-3">
                      <div className="text-xs space-y-2">
                        <div className="font-medium text-purple-800">Quality Settings Explained</div>
                        <div className="text-purple-700">
                          These settings control how your image is generated using professional photography and design principles.
                        </div>
                        <div className="grid grid-cols-2 gap-2 text-purple-600">
                          <div><strong>Quality:</strong> Resolution & detail level</div>
                          <div><strong>Style:</strong> Visual approach & aesthetics</div>
                          <div><strong>Composition:</strong> How elements are arranged</div>
                          <div><strong>Lighting:</strong> Illumination & mood</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                <div>
                  <div className="flex items-center space-x-2">
                    <Label className="text-xs font-medium text-gray-600">Image Quality</Label>
                    <OptionExplanation option={qualityOptions[imageQuality as keyof typeof qualityOptions]}>
                      <HelpCircle className="w-3 h-3 text-gray-400 cursor-help" />
                    </OptionExplanation>
                  </div>
                  <Select value={imageQuality} onValueChange={setImageQuality}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(qualityOptions).map(([key, option]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex items-center space-x-2">
                            <span>{option.icon}</span>
                            <span>{option.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="text-xs text-gray-500 mt-1">
                    {qualityOptions[imageQuality as keyof typeof qualityOptions]?.description}
                  </div>
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <Label className="text-xs font-medium text-gray-600">Style Category</Label>
                    <OptionExplanation option={styleCategories[imageStyle as keyof typeof styleCategories]}>
                      <HelpCircle className="w-3 h-3 text-gray-400 cursor-help" />
                    </OptionExplanation>
                  </div>
                  <Select value={imageStyle} onValueChange={setImageStyle}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(styleCategories).map(([key, option]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex items-center space-x-2">
                            <span>{option.icon}</span>
                            <span>{option.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="text-xs text-gray-500 mt-1">
                    {styleCategories[imageStyle as keyof typeof styleCategories]?.description}
                  </div>
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <Label className="text-xs font-medium text-gray-600">Composition Rule</Label>
                    <OptionExplanation option={compositionRules[compositionRule as keyof typeof compositionRules]}>
                      <HelpCircle className="w-3 h-3 text-gray-400 cursor-help" />
                    </OptionExplanation>
                  </div>
                  <Select value={compositionRule} onValueChange={setCompositionRule}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(compositionRules).map(([key, option]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex items-center space-x-2">
                            <span>{option.icon}</span>
                            <span>{option.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="text-xs text-gray-500 mt-1">
                    {compositionRules[compositionRule as keyof typeof compositionRules]?.description}
                  </div>
                </div>

                <div>
                  <div className="flex items-center space-x-2">
                    <Label className="text-xs font-medium text-gray-600">Lighting Preset</Label>
                    <OptionExplanation option={lightingPresets[lightingPreset as keyof typeof lightingPresets]}>
                      <HelpCircle className="w-3 h-3 text-gray-400 cursor-help" />
                    </OptionExplanation>
                  </div>
                  <Select value={lightingPreset} onValueChange={setLightingPreset}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Object.entries(lightingPresets).map(([key, option]) => (
                        <SelectItem key={key} value={key}>
                          <div className="flex items-center space-x-2">
                            <span>{option.icon}</span>
                            <span>{option.name}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <div className="text-xs text-gray-500 mt-1">
                    {lightingPresets[lightingPreset as keyof typeof lightingPresets]?.description}
                  </div>
                </div>
              </div>

              <Separator />

              {/* Brand Style Settings */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label className="text-sm font-medium">Brand Style</Label>
                  <div className="flex items-center space-x-2">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => setShowBrandDetails(!showBrandDetails)}
                    >
                      <Info className="w-4 h-4" />
                    </Button>
                    <Button variant="outline" size="sm" asChild>
                      <Link href="/dashboard/brand-assets">
                        <Palette className="w-4 h-4 mr-1" />
                        Manage
                      </Link>
                    </Button>
                  </div>
                </div>
                
                {showBrandDetails && (
                  <Card className="border-indigo-200 bg-indigo-50">
                    <CardContent className="p-3">
                      <div className="text-xs space-y-1">
                        <div className="font-medium text-indigo-800">Brand Styles</div>
                        <div className="text-indigo-700">
                          Brand styles apply consistent visual themes to your images, including color palettes and style keywords 
                          that align with your brand identity.
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                )}
                
                <Select value={selectedBrandStyle} onValueChange={setSelectedBrandStyle}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(brandStyles).map(([key, style]) => (
                      <SelectItem key={key} value={key}>
                        <div className="flex items-center space-x-2">
                          <span>{key === 'default' ? '⚪' : 
                                key === 'professional' ? '💼' : 
                                key === 'vibrant' ? '🌈' : 
                                key === 'minimal' ? '⚪' : '✨'}</span>
                          <span>{style.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                {selectedBrandStyle !== "default" && (
                  <Card className="border-indigo-200 bg-indigo-50">
                    <CardContent className="p-3">
                      <div className="space-y-3">
                        <div>
                          <div className="text-xs font-medium text-indigo-800 mb-1">Style Description</div>
                          <p className="text-xs text-indigo-700">
                            {brandStyles[selectedBrandStyle as keyof typeof brandStyles].description}
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <span className="text-xs font-medium text-indigo-800">Colors:</span>
                          <div className="flex space-x-1">
                            {brandStyles[selectedBrandStyle as keyof typeof brandStyles].colors.map((color, i) => (
                              <div
                                key={i}
                                className="w-4 h-4 rounded border border-indigo-300"
                                style={{ backgroundColor: color }}
                                title={color}
                              />
                            ))}
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2">
                          <Switch
                            id="apply-brand-colors"
                            checked={applyBrandColors}
                            onCheckedChange={setApplyBrandColors}
                          />
                          <Label htmlFor="apply-brand-colors" className="text-xs text-indigo-700">
                            Apply brand colors to generation
                          </Label>
                        </div>
                        
                        {applyBrandColors && (
                          <div className="text-xs text-indigo-600 bg-indigo-100 p-2 rounded">
                            <strong>Active:</strong> Brand colors will be incorporated into your image generation
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <main className="flex-1 p-6">
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Brand-Aware Prompt Enhancement */}
              <Card className="mb-6">
                <CardContent className="p-4">
                  <BrandAwareGenerate
                    prompt={prompt}
                    setPrompt={setPrompt}
                    onGenerate={() => {}}
                    // Custom handlers to sync state
                    setEnhancedPrompt={setEnhancedPrompt}
                    setSelectedBrandId={setSelectedBrandId}
                    setSelectedBrand={setSelectedBrand}
                  />
                </CardContent>
              </Card>
              {/* Generation Form */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Sparkles className="w-5 h-5 mr-2" />
                    Generate Images
                  </CardTitle>
                  <CardDescription>
                    Create stunning, on-brand visuals with AI-powered generation
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label htmlFor="prompt">Prompt</Label>
                    <Textarea
                      id="prompt"
                      placeholder="Describe the image you want to generate..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      className="mt-2"
                      rows={3}
                    />
                  </div>

                  <div>
                    <Label htmlFor="negative-prompt">Negative Prompt (Optional)</Label>
                    <Textarea
                      id="negative-prompt"
                      placeholder="Describe what you don't want in the image..."
                      value={negativePrompt}
                      onChange={(e) => setNegativePrompt(e.target.value)}
                      className="mt-2"
                      rows={2}
                    />
                  </div>

                  {/* Generation Summary */}
                  <Card className="mb-4 border-gray-200 bg-gray-50">
                    <CardContent className="p-4">
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="text-sm font-medium text-gray-800">Generation Settings</div>
                          <div className="text-sm font-medium text-gray-800">
                            Est. Cost: ${(0.04 * numImages).toFixed(2)}
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-3 text-xs">
                          <div className="space-y-1">
                            <div className="flex items-center space-x-1">
                              <span>{qualityOptions[imageQuality as keyof typeof qualityOptions]?.icon}</span>
                              <span className="font-medium">Quality:</span>
                              <span>{qualityOptions[imageQuality as keyof typeof qualityOptions]?.name}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span>{styleCategories[imageStyle as keyof typeof styleCategories]?.icon}</span>
                              <span className="font-medium">Style:</span>
                              <span>{styleCategories[imageStyle as keyof typeof styleCategories]?.name}</span>
                            </div>
                          </div>
                          
                          <div className="space-y-1">
                            <div className="flex items-center space-x-1">
                              <span>{compositionRules[compositionRule as keyof typeof compositionRules]?.icon}</span>
                              <span className="font-medium">Composition:</span>
                              <span>{compositionRules[compositionRule as keyof typeof compositionRules]?.name}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <span>{lightingPresets[lightingPreset as keyof typeof lightingPresets]?.icon}</span>
                              <span className="font-medium">Lighting:</span>
                              <span>{lightingPresets[lightingPreset as keyof typeof lightingPresets]?.name}</span>
                            </div>
                          </div>
                        </div>
                        
                        {selectedTemplate && (
                          <div className="flex items-center space-x-1 text-xs text-green-700 bg-green-100 p-2 rounded">
                            <Star className="w-3 h-3" />
                            <span className="font-medium">Template Active:</span>
                            <span>{selectedTemplate.name}</span>
                          </div>
                        )}
                        
                        {selectedBrandStyle !== "default" && (
                          <div className="flex items-center space-x-1 text-xs text-indigo-700 bg-indigo-100 p-2 rounded">
                            <Palette className="w-3 h-3" />
                            <span className="font-medium">Brand Style:</span>
                            <span>{brandStyles[selectedBrandStyle as keyof typeof brandStyles].name}</span>
                            {applyBrandColors && <span>(with colors)</span>}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>

                  <Button 
                    onClick={generateImages} 
                    disabled={isGenerating || !prompt.trim()}
                    className="w-full"
                    size="lg"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate {numImages} Image{numImages > 1 ? 's' : ''} 
                        {imageQuality === 'professional' && <span className="ml-1">✨</span>}
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>

              {/* Results */}
              {generatedImages.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span>Generated Images</span>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        {processingTime > 0 && (
                          <span>Time: {processingTime.toFixed(1)}s</span>
                        )}
                        {totalCost > 0 && (
                          <span>Cost: ${totalCost.toFixed(2)}</span>
                        )}
                      </div>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {generatedImages.map((image) => (
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
                            <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                              {image.prompt}
                            </p>
                            <div className="flex items-center justify-between">
                              <div className="flex space-x-2">
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => downloadImage(image)}
                                >
                                  <Download className="w-4 h-4" />
                                </Button>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => copyPrompt(image)}
                                >
                                  <Copy className="w-4 h-4" />
                                </Button>
                              </div>
                              <Badge variant="secondary" className="text-xs">
                                {image.size}
                              </Badge>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Generation Status */}
              {isGenerating && (
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <Loader2 className="w-6 h-6 animate-spin text-blue-600" />
                      <div className="flex-1">
                        <div className="text-sm font-medium">Generating images...</div>
                        <div className="text-xs text-gray-500">
                          This may take a few moments
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
              {campaign && (
                <Card className="mb-6 border-indigo-300 bg-indigo-50">
                  <CardContent className="p-4">
                    <div className="flex items-center space-x-4">
                      <Target className="w-6 h-6 text-indigo-600" />
                      <div>
                        <div className="font-semibold text-indigo-800">Generating for Campaign:</div>
                        <div className="text-indigo-700">{campaign.name}</div>
                        <div className="text-xs text-indigo-600">{campaign.description}</div>
                      </div>
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
