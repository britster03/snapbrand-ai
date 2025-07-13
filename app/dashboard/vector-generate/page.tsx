"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"
import { 
  Sparkles, 
  Download, 
  Copy, 
  RefreshCw, 
  Palette,
  Settings,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2,
  Eye,
  Info,
  HelpCircle,
  ArrowLeft,
  FileImage,
  LogOut,
  User
} from "lucide-react"
import { toast } from "sonner"
import Link from "next/link"
import { ProtectedRoute } from "@/components/protected-route"
import { LoadingIndicator } from "@/components/ui/loading-indicator"
import { useAuth } from "@/components/auth-context"
import { useRouter } from "next/navigation"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

import { 
  apiClient, 
  type VectorGenerateRequest, 
  type GeneratedVector, 
  type VectorGenerateResponse 
} from "@/lib/api"

const vectorStyles = {
  modern: {
    name: "Modern",
    description: "Clean, contemporary design",
    icon: "🎯",
    examples: ["Corporate logos", "App icons", "Brand elements"]
  },
  minimalist: {
    name: "Minimalist",
    description: "Simple, clean lines",
    icon: "⚪",
    examples: ["Simple icons", "Clean graphics", "Subtle designs"]
  },
  artistic: {
    name: "Artistic",
    description: "Creative and expressive",
    icon: "🎨",
    examples: ["Illustrations", "Creative graphics", "Artistic elements"]
  },
  geometric: {
    name: "Geometric",
    description: "Sharp, angular shapes",
    icon: "🔷",
    examples: ["Abstract patterns", "Geometric icons", "Technical graphics"]
  },
  organic: {
    name: "Organic",
    description: "Natural, flowing forms",
    icon: "🌿",
    examples: ["Nature-inspired", "Flowing shapes", "Organic patterns"]
  }
}

const vectorSizes = {
  "256x256": { name: "Small", description: "256×256 pixels" },
  "512x512": { name: "Medium", description: "512×512 pixels" },
  "1024x1024": { name: "Large", description: "1024×1024 pixels" },
  "2048x2048": { name: "Extra Large", description: "2048×2048 pixels" }
}

export default function VectorGeneratePage() {
  const router = useRouter()
  const { user, logout } = useAuth()
  
  const [prompt, setPrompt] = useState("")
  const [negativePrompt, setNegativePrompt] = useState("")
  const [numImages, setNumImages] = useState(1)
  const [size, setSize] = useState("512x512")
  const [style, setStyle] = useState("modern")
  const [seed, setSeed] = useState<number | undefined>(undefined)
  const [format, setFormat] = useState<'svg' | 'base64'>('svg')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedVectors, setGeneratedVectors] = useState<GeneratedVector[]>([])
  const [showAdvanced, setShowAdvanced] = useState(false)

  const generateVectors = async () => {
    if (!prompt.trim()) {
      toast.error("Please enter a prompt")
      return
    }

    setIsGenerating(true)
    try {
      const request: VectorGenerateRequest = {
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim() || undefined,
        num_images: numImages,
        size,
        style,
        seed,
        format
      }

      const response: VectorGenerateResponse = await apiClient.generateVectorImages(request)
      
      setGeneratedVectors(response.vectors)
      toast.success(`Generated ${response.vectors.length} vector image${response.vectors.length > 1 ? 's' : ''}`)
      
      if (response.total_cost) {
        toast.info(`Estimated cost: $${response.total_cost.toFixed(3)}`)
      }
    } catch (error) {
      console.error('Vector generation failed:', error)
      toast.error("Failed to generate vector images. Please try again.")
    } finally {
      setIsGenerating(false)
    }
  }

  const downloadVector = (vector: GeneratedVector) => {
    try {
      let content = ''
      let filename = `vector_${vector.id}.svg`
      
      if (vector.svg_content) {
        content = vector.svg_content
      } else if (vector.svg_base64) {
        content = atob(vector.svg_base64)
      } else {
        toast.error("No vector content available for download")
        return
      }

      const blob = new Blob([content], { type: 'image/svg+xml' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.style.display = 'none'
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      
      toast.success("Vector downloaded successfully")
    } catch (error) {
      console.error('Download failed:', error)
      toast.error("Failed to download vector")
    }
  }

  const copyPrompt = (vector: GeneratedVector) => {
    navigator.clipboard.writeText(vector.prompt)
    toast.success("Prompt copied to clipboard")
  }

  const generateRandomSeed = () => {
    setSeed(Math.floor(Math.random() * 1000000))
  }

  const resetForm = () => {
    setPrompt("")
    setNegativePrompt("")
    setNumImages(1)
    setSize("512x512")
    setStyle("modern")
    setSeed(undefined)
    setFormat('svg')
    setGeneratedVectors([])
  }

  const handleLogout = () => {
    logout()
    router.push("/login")
    toast.success("Logged out successfully")
  }

  const renderVector = (vector: GeneratedVector) => {
    let svgContent = ''
    
    if (vector.svg_content) {
      svgContent = vector.svg_content
    } else if (vector.svg_base64) {
      svgContent = atob(vector.svg_base64)
    }

    if (svgContent) {
      return (
        <div 
          className="w-full h-full bg-white rounded-lg border border-gray-200 p-4 flex items-center justify-center"
          dangerouslySetInnerHTML={{ __html: svgContent }}
        />
      )
    }

    return (
      <div className="w-full h-full bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
        <FileImage className="w-8 h-8 text-gray-400" />
      </div>
    )
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <header className="bg-white border-b">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link href="/dashboard" className="flex items-center space-x-2 text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-5 h-5" />
                <span>Back to Dashboard</span>
              </Link>
              <div className="h-6 w-px bg-gray-300" />
              <div className="flex items-center space-x-2">
                <Palette className="w-6 h-6 text-purple-600" />
                <h1 className="text-xl font-semibold">Vector Image Generator</h1>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-purple-100 text-purple-700">
                Vector AI
              </Badge>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="sm" className="flex items-center space-x-2">
                    <User className="w-4 h-4" />
                    <span className="hidden sm:inline">{user?.username || "User"}</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="w-4 h-4 mr-2" />
                    Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        <div className="container mx-auto px-6 py-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Generation Controls */}
            <div className="lg:col-span-1 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2">
                    <Sparkles className="w-5 h-5" />
                    <span>Vector Generation</span>
                  </CardTitle>
                  <CardDescription>
                    Generate scalable vector graphics from text descriptions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Prompt */}
                  <div className="space-y-2">
                    <Label htmlFor="prompt">Prompt</Label>
                    <Textarea
                      id="prompt"
                      placeholder="Describe the vector image you want to create..."
                      value={prompt}
                      onChange={(e) => setPrompt(e.target.value)}
                      className="min-h-[100px]"
                    />
                  </div>

                  {/* Style Selection */}
                  <div className="space-y-2">
                    <Label htmlFor="style">Style</Label>
                    <Select value={style} onValueChange={setStyle}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select style" />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(vectorStyles).map(([key, styleInfo]) => (
                          <SelectItem key={key} value={key}>
                            <div className="flex items-center space-x-2">
                              <span>{styleInfo.icon}</span>
                              <span>{styleInfo.name}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-gray-600">
                      {vectorStyles[style as keyof typeof vectorStyles]?.description}
                    </p>
                  </div>

                  {/* Basic Settings */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="numImages">Number of Images</Label>
                      <Select value={numImages.toString()} onValueChange={(v) => setNumImages(parseInt(v))}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {[1, 2, 3, 4].map(n => (
                            <SelectItem key={n} value={n.toString()}>{n}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="size">Size</Label>
                      <Select value={size} onValueChange={setSize}>
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(vectorSizes).map(([key, sizeInfo]) => (
                            <SelectItem key={key} value={key}>
                              {sizeInfo.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {/* Advanced Settings Toggle */}
                  <div className="flex items-center space-x-2">
                    <Switch
                      id="advanced"
                      checked={showAdvanced}
                      onCheckedChange={setShowAdvanced}
                    />
                    <Label htmlFor="advanced">Advanced Settings</Label>
                  </div>

                  {/* Advanced Settings */}
                  {showAdvanced && (
                    <div className="space-y-4 pt-4 border-t">
                      <div className="space-y-2">
                        <Label htmlFor="negative-prompt">Negative Prompt</Label>
                        <Textarea
                          id="negative-prompt"
                          placeholder="What to avoid in the vector..."
                          value={negativePrompt}
                          onChange={(e) => setNegativePrompt(e.target.value)}
                          className="min-h-[80px]"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="seed">Seed (Optional)</Label>
                        <div className="flex space-x-2">
                          <Input
                            id="seed"
                            type="number"
                            placeholder="Random seed"
                            value={seed || ''}
                            onChange={(e) => setSeed(e.target.value ? parseInt(e.target.value) : undefined)}
                          />
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={generateRandomSeed}
                          >
                            <RefreshCw className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="format">Output Format</Label>
                        <Select value={format} onValueChange={(v) => setFormat(v as 'svg' | 'base64')}>
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="svg">SVG (Raw)</SelectItem>
                            <SelectItem value="base64">Base64 Encoded</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex space-x-2">
                    <Button
                      onClick={generateVectors}
                      disabled={isGenerating || !prompt.trim()}
                      className="flex-1"
                    >
                      {isGenerating ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Zap className="w-4 h-4 mr-2" />
                          Generate Vectors
                        </>
                      )}
                    </Button>
                    <Button
                      variant="outline"
                      onClick={resetForm}
                      disabled={isGenerating}
                    >
                      Reset
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Results */}
            <div className="lg:col-span-2">
              {/* Loading Animation */}
              <LoadingIndicator 
                isLoading={isGenerating} 
                numImages={numImages} 
                prompt={prompt}
                onComplete={() => {
                  console.log("Vector generation animation completed")
                }}
              />
              
              {!isGenerating && (
                <Card>
                  <CardHeader>
                    <CardTitle>Generated Vectors</CardTitle>
                    <CardDescription>
                      Your AI-generated vector images will appear here
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {generatedVectors.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {generatedVectors.map((vector, index) => (
                        <div key={vector.id} className="space-y-4">
                          <div className="aspect-square">
                            {renderVector(vector)}
                          </div>
                          
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                              <Badge variant="outline">{vector.style}</Badge>
                              <Badge variant="outline">{vector.size}</Badge>
                            </div>
                            <div className="flex items-center space-x-2">
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Button
                                      variant="outline"
                                      size="sm"
                                      onClick={() => copyPrompt(vector)}
                                    >
                                      <Copy className="w-4 h-4" />
                                    </Button>
                                  </TooltipTrigger>
                                  <TooltipContent>Copy prompt</TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                              
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => downloadVector(vector)}
                              >
                                <Download className="w-4 h-4 mr-2" />
                                Download
                              </Button>
                            </div>
                          </div>
                          
                          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
                            <strong>Prompt:</strong> {vector.prompt}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-12">
                      <Palette className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">
                        No vectors generated yet
                      </h3>
                      <p className="text-gray-600 mb-4">
                        Enter a prompt and click "Generate Vectors" to create your first vector image.
                      </p>
                    </div>
                  )}
                </CardContent>
              </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
} 