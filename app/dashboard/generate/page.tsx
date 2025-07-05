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
  Loader2
} from "lucide-react"
import { toast } from "sonner"
import Image from "next/image"
import Link from "next/link"

import { 
  apiClient, 
  type GenerateRequest, 
  type GeneratedImage, 
  type Template 
} from "@/lib/api"

export default function GeneratePage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null)
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  
  const [prompt, setPrompt] = useState("")
  const [negativePrompt, setNegativePrompt] = useState("")
  const [numImages, setNumImages] = useState(1)
  const [size, setSize] = useState("1024x1024")
  const [guidanceScale, setGuidanceScale] = useState(7.5)
  const [seed, setSeed] = useState<number | undefined>()
  
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImages, setGeneratedImages] = useState<GeneratedImage[]>([])
  const [processingTime, setProcessingTime] = useState<number>(0)
  const [totalCost, setTotalCost] = useState<number>(0)

  // Load templates on component mount
  useEffect(() => {
    loadTemplates()
    loadCategories()
  }, [])

  const loadTemplates = async () => {
    try {
      const templateList = await apiClient.getTemplates(selectedCategory || undefined)
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
    const template = templates.find(t => t.id === templateId)
    if (template) {
      setSelectedTemplate(template)
      setSize(template.default_size)
      if (template.negative_prompt) {
        setNegativePrompt(template.negative_prompt)
      }
    }
  }

  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    setSelectedTemplate(null)
  }

  const generateImages = async () => {
    if (!prompt.trim()) {
      toast.error("Please enter a prompt")
      return
    }

    setIsGenerating(true)
    setGeneratedImages([])
    setProcessingTime(0)
    setTotalCost(0)

    try {
      const request: GenerateRequest = {
        prompt: prompt.trim(),
        negative_prompt: negativePrompt.trim() || undefined,
        num_images: numImages,
        size,
        guidance_scale: guidanceScale,
        seed: seed || undefined,
        template_id: selectedTemplate?.id,
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
                SnapBrand.ai
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
                  <SelectItem value="">All categories</SelectItem>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label className="text-sm font-medium">Template</Label>
              <Select value={selectedTemplate?.id || ""} onValueChange={handleTemplateSelect}>
                <SelectTrigger className="mt-2">
                  <SelectValue placeholder="Choose a template" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((template) => (
                    <SelectItem key={template.id} value={template.id}>
                      {template.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {selectedTemplate && (
              <Card className="border-blue-200 bg-blue-50">
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm">{selectedTemplate.name}</CardTitle>
                  <CardDescription className="text-xs">
                    {selectedTemplate.description}
                  </CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="text-xs text-gray-600">
                    <div><strong>Category:</strong> {selectedTemplate.category}</div>
                    <div><strong>Size:</strong> {selectedTemplate.default_size}</div>
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
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <div className="max-w-4xl mx-auto space-y-6">
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
                      Generate Images
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
          </div>
        </main>
      </div>
    </div>
  )
}
