"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
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
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { Input } from "@/components/ui/input"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  const recentImages = [
    { id: 1, name: "Product Hero Shot", template: "E-commerce", status: "completed", date: "2 hours ago" },
    { id: 2, name: "Instagram Story", template: "Social Media", status: "processing", date: "5 hours ago" },
    { id: 3, name: "Email Header", template: "Marketing", status: "completed", date: "1 day ago" },
    { id: 4, name: "Website Banner", template: "Web", status: "completed", date: "2 days ago" },
  ]

  const templates = [
    { id: 1, name: "Product Hero Shot", category: "E-commerce", uses: 1250 },
    { id: 2, name: "Instagram Post", category: "Social Media", uses: 980 },
    { id: 3, name: "Email Header", category: "Marketing", uses: 750 },
    { id: 4, name: "Website Banner", category: "Web", uses: 650 },
    { id: 5, name: "LinkedIn Post", category: "Social Media", uses: 420 },
    { id: 6, name: "Product Catalog", category: "E-commerce", uses: 380 },
  ]

  return (
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
              Pro Plan
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
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Images Generated</CardTitle>
                    <ImageIcon className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">1,234</div>
                    <p className="text-xs text-muted-foreground">+20% from last month</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Credits Used</CardTitle>
                    <Zap className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">342</div>
                    <p className="text-xs text-muted-foreground">158 remaining</p>
                    <Progress value={68} className="mt-2" />
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Downloads</CardTitle>
                    <Download className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">892</div>
                    <p className="text-xs text-muted-foreground">+12% from last month</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Active Templates</CardTitle>
                    <Grid3X3 className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">24</div>
                    <p className="text-xs text-muted-foreground">6 custom templates</p>
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
                    {recentImages.map((image) => (
                      <div key={image.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div className="flex items-center space-x-4">
                          <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg flex items-center justify-center">
                            <ImageIcon className="w-6 h-6 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-medium">{image.name}</h3>
                            <p className="text-sm text-gray-500">
                              {image.template} • {image.date}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge variant={image.status === "completed" ? "default" : "secondary"}>{image.status}</Badge>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm">
                                <MoreHorizontal className="w-4 h-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent>
                              <DropdownMenuItem>View</DropdownMenuItem>
                              <DropdownMenuItem>Download</DropdownMenuItem>
                              <DropdownMenuItem>Edit</DropdownMenuItem>
                              <DropdownMenuItem>Delete</DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {activeTab === "gallery" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Image Gallery</h1>
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                    <Input placeholder="Search images..." className="pl-10 w-64" />
                  </div>
                  <Button variant="outline">
                    <Filter className="w-4 h-4 mr-2" />
                    Filter
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {Array.from({ length: 12 }).map((_, i) => (
                  <Card key={i} className="overflow-hidden group cursor-pointer hover:shadow-lg transition-shadow">
                    <div className="relative">
                      <Image
                        src={`/placeholder.svg?height=300&width=300`}
                        alt={`Generated image ${i + 1}`}
                        width={300}
                        height={300}
                        className="w-full h-48 object-cover"
                      />
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                        <div className="flex space-x-2">
                          <Button size="sm" variant="secondary">
                            <Download className="w-4 h-4" />
                          </Button>
                          <Button size="sm" variant="secondary">
                            View
                          </Button>
                        </div>
                      </div>
                    </div>
                    <CardContent className="p-4">
                      <h3 className="font-medium mb-1">Product Hero Shot</h3>
                      <p className="text-sm text-gray-500">E-commerce Template</p>
                      <div className="flex items-center justify-between mt-2">
                        <Badge variant="secondary" className="text-xs">
                          1024x1024
                        </Badge>
                        <span className="text-xs text-gray-500">2 hours ago</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          )}

          {activeTab === "templates" && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold">Templates</h1>
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
                  <TabsTrigger value="web">Web</TabsTrigger>
                </TabsList>
                <TabsContent value="all" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {templates.map((template) => (
                      <Card key={template.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">{template.name}</CardTitle>
                            <Badge variant="outline">{template.category}</Badge>
                          </div>
                          <CardDescription>Used {template.uses.toLocaleString()} times</CardDescription>
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
                    ))}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}
