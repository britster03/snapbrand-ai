"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Upload, Palette, ImageIcon, Type, ArrowLeft, Plus, Edit, Download, Eye, Copy, Check } from "lucide-react"
import Link from "next/link"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export default function BrandAssetsPage() {
  const [activeTab, setActiveTab] = useState("overview")
  const [copiedColor, setCopiedColor] = useState<string | null>(null)

  const brandColors = [
    { name: "Primary Blue", hex: "#3B82F6", usage: "Primary buttons, links" },
    { name: "Secondary Purple", hex: "#8B5CF6", usage: "Accents, highlights" },
    { name: "Success Green", hex: "#10B981", usage: "Success states" },
    { name: "Warning Orange", hex: "#F59E0B", usage: "Warnings, alerts" },
    { name: "Error Red", hex: "#EF4444", usage: "Error states" },
    { name: "Neutral Gray", hex: "#6B7280", usage: "Text, borders" },
  ]

  const logos = [
    { id: 1, name: "Primary Logo", type: "SVG", size: "2.4 KB", uploaded: "2 days ago" },
    { id: 2, name: "Logo Mark", type: "PNG", size: "45 KB", uploaded: "2 days ago" },
    { id: 3, name: "White Logo", type: "SVG", size: "2.1 KB", uploaded: "2 days ago" },
    { id: 4, name: "Favicon", type: "ICO", size: "15 KB", uploaded: "1 week ago" },
  ]

  const sampleImages = [
    { id: 1, name: "Product Photography Style", category: "Photography", uploaded: "3 days ago" },
    { id: 2, name: "Lifestyle Scene", category: "Photography", uploaded: "3 days ago" },
    { id: 3, name: "Brand Illustration", category: "Illustration", uploaded: "1 week ago" },
    { id: 4, name: "Icon Style Guide", category: "Icons", uploaded: "1 week ago" },
  ]

  const fonts = [
    { name: "Inter", type: "Primary", usage: "Headings, UI elements", weight: "400, 500, 600, 700" },
    { name: "Source Sans Pro", type: "Secondary", usage: "Body text, descriptions", weight: "400, 600" },
    { name: "JetBrains Mono", type: "Monospace", usage: "Code, technical content", weight: "400, 500" },
  ]

  const copyToClipboard = (color: string) => {
    navigator.clipboard.writeText(color)
    setCopiedColor(color)
    setTimeout(() => setCopiedColor(null), 2000)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button variant="ghost" size="sm" asChild>
              <Link href="/dashboard">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Link>
            </Button>
            <div className="h-6 w-px bg-gray-300" />
            <h1 className="text-xl font-semibold">Brand Assets</h1>
          </div>
          <Button>
            <Upload className="w-4 h-4 mr-2" />
            Upload Assets
          </Button>
        </div>
      </header>

      <div className="p-6 space-y-6">
        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Assets</CardTitle>
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">24</div>
              <p className="text-xs text-muted-foreground">+3 this week</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Brand Colors</CardTitle>
              <Palette className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">6</div>
              <p className="text-xs text-muted-foreground">Primary palette</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Logos</CardTitle>
              <ImageIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">4</div>
              <p className="text-xs text-muted-foreground">All formats</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Fonts</CardTitle>
              <Type className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">Typography system</p>
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue="colors" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="colors">Brand Colors</TabsTrigger>
            <TabsTrigger value="logos">Logos</TabsTrigger>
            <TabsTrigger value="images">Sample Images</TabsTrigger>
            <TabsTrigger value="fonts">Typography</TabsTrigger>
          </TabsList>

          <TabsContent value="colors" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Brand Colors</h2>
                <p className="text-gray-600">Your brand's color palette used for consistent image generation</p>
              </div>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Color
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {brandColors.map((color, index) => (
                <Card key={index} className="overflow-hidden">
                  <div className="h-32 w-full" style={{ backgroundColor: color.hex }} />
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{color.name}</h3>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem>Edit</DropdownMenuItem>
                          <DropdownMenuItem>Duplicate</DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                    <div className="flex items-center justify-between mb-2">
                      <code className="text-sm bg-gray-100 px-2 py-1 rounded">{color.hex}</code>
                      <Button variant="ghost" size="sm" onClick={() => copyToClipboard(color.hex)}>
                        {copiedColor === color.hex ? (
                          <Check className="w-4 h-4 text-green-600" />
                        ) : (
                          <Copy className="w-4 h-4" />
                        )}
                      </Button>
                    </div>
                    <p className="text-sm text-gray-500">{color.usage}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="logos" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Logo Assets</h2>
                <p className="text-gray-600">Your brand logos in various formats and styles</p>
              </div>
              <Button>
                <Upload className="w-4 h-4 mr-2" />
                Upload Logo
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {logos.map((logo) => (
                <Card key={logo.id}>
                  <CardContent className="p-4">
                    <div className="w-full h-32 bg-gray-100 rounded-lg flex items-center justify-center mb-4">
                      <ImageIcon className="w-8 h-8 text-gray-400" />
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-medium">{logo.name}</h3>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>{logo.type}</span>
                        <span>{logo.size}</span>
                      </div>
                      <p className="text-xs text-gray-400">{logo.uploaded}</p>
                      <div className="flex space-x-2 pt-2">
                        <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="images" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Sample Images</h2>
                <p className="text-gray-600">Reference images that define your brand's visual style</p>
              </div>
              <Button>
                <Upload className="w-4 h-4 mr-2" />
                Upload Images
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {sampleImages.map((image) => (
                <Card key={image.id} className="overflow-hidden">
                  <div className="w-full h-48 bg-gradient-to-br from-blue-100 to-purple-100 flex items-center justify-center">
                    <ImageIcon className="w-8 h-8 text-blue-600" />
                  </div>
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h3 className="font-medium">{image.name}</h3>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="sm">
                              <Edit className="w-4 h-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent>
                            <DropdownMenuItem>View</DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Download</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {image.category}
                      </Badge>
                      <p className="text-xs text-gray-400">{image.uploaded}</p>
                      <div className="flex space-x-2 pt-2">
                        <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                          <Eye className="w-4 h-4 mr-1" />
                          View
                        </Button>
                        <Button variant="outline" size="sm" className="flex-1 bg-transparent">
                          <Download className="w-4 h-4 mr-1" />
                          Download
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="fonts" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">Typography</h2>
                <p className="text-gray-600">Font families and styles used in your brand</p>
              </div>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Add Font
              </Button>
            </div>

            <div className="space-y-4">
              {fonts.map((font, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-2">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-2xl font-bold" style={{ fontFamily: font.name }}>
                            {font.name}
                          </h3>
                          <Badge variant="outline">{font.type}</Badge>
                        </div>
                        <p className="text-gray-600">{font.usage}</p>
                        <p className="text-sm text-gray-500">Weights: {font.weight}</p>
                        <div className="text-lg" style={{ fontFamily: font.name }}>
                          The quick brown fox jumps over the lazy dog
                        </div>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent>
                          <DropdownMenuItem>Edit</DropdownMenuItem>
                          <DropdownMenuItem>Download</DropdownMenuItem>
                          <DropdownMenuItem className="text-red-600">Remove</DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
