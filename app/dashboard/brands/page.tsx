"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Plus, Upload, TrendingUp, Eye, Edit, Trash2, Sparkles, Zap, Building2, Heart, Coffee, Briefcase, Stethoscope, GraduationCap, Home, Car, Shirt, Laptop, Wrench, Star, Award, Brain, Camera, MoreHorizontal, Search, Filter, SortDesc } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/components/ui/use-toast"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { apiClient } from "@/lib/api"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

// Form validation schema
const brandFormSchema = z.object({
  name: z.string().min(1, "Brand name is required"),
  description: z.string().optional(),
  industry: z.enum([
    "e-commerce",
    "saas",
    "healthcare",
    "finance",
    "education",
    "real-estate",
    "retail",
    "hospitality",
    "technology",
    "fashion",
    "food",
    "automotive",
    "other"
  ]),
  visual_style: z.string().optional(),
  brand_keywords: z.string().optional(),
})

interface BrandProfile {
  id: number
  name: string
  description?: string
  industry: string
  visual_style?: string
  primary_colors: string[]
  total_generations: number
  successful_campaigns: number
  created_at: string
}

const industryConfig = {
  "e-commerce": { icon: Briefcase, gradient: "from-blue-500 to-cyan-500", bgColor: "bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-blue-950/20 dark:to-cyan-950/20", hoverGradient: "from-blue-600 to-cyan-600", accent: "text-blue-600", border: "border-blue-200" },
  "saas": { icon: Laptop, gradient: "from-purple-500 to-pink-500", bgColor: "bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-950/20 dark:to-pink-950/20", hoverGradient: "from-purple-600 to-pink-600", accent: "text-purple-600", border: "border-purple-200" },
  "healthcare": { icon: Stethoscope, gradient: "from-green-500 to-emerald-500", bgColor: "bg-gradient-to-br from-green-50 to-emerald-50 dark:from-green-950/20 dark:to-emerald-950/20", hoverGradient: "from-green-600 to-emerald-600", accent: "text-green-600", border: "border-green-200" },
  "finance": { icon: TrendingUp, gradient: "from-yellow-500 to-orange-500", bgColor: "bg-gradient-to-br from-yellow-50 to-orange-50 dark:from-yellow-950/20 dark:to-orange-950/20", hoverGradient: "from-yellow-600 to-orange-600", accent: "text-yellow-600", border: "border-yellow-200" },
  "education": { icon: GraduationCap, gradient: "from-indigo-500 to-blue-500", bgColor: "bg-gradient-to-br from-indigo-50 to-blue-50 dark:from-indigo-950/20 dark:to-blue-950/20", hoverGradient: "from-indigo-600 to-blue-600", accent: "text-indigo-600", border: "border-indigo-200" },
  "real-estate": { icon: Home, gradient: "from-red-500 to-pink-500", bgColor: "bg-gradient-to-br from-red-50 to-pink-50 dark:from-red-950/20 dark:to-pink-950/20", hoverGradient: "from-red-600 to-pink-600", accent: "text-red-600", border: "border-red-200" },
  "retail": { icon: Building2, gradient: "from-teal-500 to-green-500", bgColor: "bg-gradient-to-br from-teal-50 to-green-50 dark:from-teal-950/20 dark:to-green-950/20", hoverGradient: "from-teal-600 to-green-600", accent: "text-teal-600", border: "border-teal-200" },
  "hospitality": { icon: Coffee, gradient: "from-amber-500 to-orange-500", bgColor: "bg-gradient-to-br from-amber-50 to-orange-50 dark:from-amber-950/20 dark:to-orange-950/20", hoverGradient: "from-amber-600 to-orange-600", accent: "text-amber-600", border: "border-amber-200" },
  "technology": { icon: Zap, gradient: "from-violet-500 to-purple-500", bgColor: "bg-gradient-to-br from-violet-50 to-purple-50 dark:from-violet-950/20 dark:to-purple-950/20", hoverGradient: "from-violet-600 to-purple-600", accent: "text-violet-600", border: "border-violet-200" },
  "fashion": { icon: Shirt, gradient: "from-pink-500 to-rose-500", bgColor: "bg-gradient-to-br from-pink-50 to-rose-50 dark:from-pink-950/20 dark:to-rose-950/20", hoverGradient: "from-pink-600 to-rose-600", accent: "text-pink-600", border: "border-pink-200" },
  "food": { icon: Heart, gradient: "from-orange-500 to-red-500", bgColor: "bg-gradient-to-br from-orange-50 to-red-50 dark:from-orange-950/20 dark:to-red-950/20", hoverGradient: "from-orange-600 to-red-600", accent: "text-orange-600", border: "border-orange-200" },
  "automotive": { icon: Car, gradient: "from-slate-500 to-gray-500", bgColor: "bg-gradient-to-br from-slate-50 to-gray-50 dark:from-slate-950/20 dark:to-gray-950/20", hoverGradient: "from-slate-600 to-gray-600", accent: "text-slate-600", border: "border-slate-200" },
  "other": { icon: Wrench, gradient: "from-gray-500 to-slate-500", bgColor: "bg-gradient-to-br from-gray-50 to-slate-50 dark:from-gray-950/20 dark:to-slate-950/20", hoverGradient: "from-gray-600 to-slate-600", accent: "text-gray-600", border: "border-gray-200" }
}

const visualStyleConfig = {
  "modern": { emoji: "✨", color: "text-blue-600", bg: "bg-blue-50" },
  "classic": { emoji: "🎩", color: "text-amber-600", bg: "bg-amber-50" },
  "bold": { emoji: "🔥", color: "text-red-600", bg: "bg-red-50" },
  "playful": { emoji: "🎨", color: "text-purple-600", bg: "bg-purple-50" },
  "professional": { emoji: "💼", color: "text-slate-600", bg: "bg-slate-50" },
  "minimal": { emoji: "⚪", color: "text-gray-600", bg: "bg-gray-50" },
  "luxury": { emoji: "👑", color: "text-yellow-600", bg: "bg-yellow-50" }
}

export default function BrandsPage() {
  const [brands, setBrands] = useState<BrandProfile[]>([])
  const [loading, setLoading] = useState(true)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [sortBy, setSortBy] = useState("created_at")
  const [filterIndustry, setFilterIndustry] = useState("all")
  const router = useRouter()
  const { toast } = useToast()

  const form = useForm<z.infer<typeof brandFormSchema>>({
    resolver: zodResolver(brandFormSchema),
    defaultValues: {
      name: "",
      description: "",
      industry: "other",
      visual_style: "",
      brand_keywords: "",
    },
  })

  useEffect(() => {
    fetchBrands()
  }, [])

  const fetchBrands = async () => {
    try {
      const token = apiClient.getAccessToken()
      
      if (!token || token === "null" || token === "undefined") {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      const data = await apiClient.getBrandProfiles()
      setBrands(data)
      
    } catch (error: any) {
      console.error("Error fetching brands:", error)
      
      if (error.status === 401) {
        toast({
          title: "Authentication Error",
          description: "Session expired. Please login again",
          variant: "destructive",
        })
        apiClient.clearAccessToken()
        router.push("/login")
      } else {
        toast({
          title: "Error",
          description: error.message || "Failed to fetch brand profiles",
          variant: "destructive",
        })
      }
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (values: z.infer<typeof brandFormSchema>) => {
    try {
      const token = apiClient.getAccessToken()
      
      if (!token || token === "null" || token === "undefined") {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      const brandData = {
        ...values,
        brand_keywords: values.brand_keywords?.split(",").map(k => k.trim()).filter(k => k) || [],
      }

      const newBrand = await apiClient.createBrandProfile(brandData)
      
      toast({
        title: "Success!",
        description: "Brand profile created successfully",
      })
      setCreateDialogOpen(false)
      form.reset()
      fetchBrands()
      
    } catch (error: any) {
      console.error("Error creating brand:", error)
      
      if (error.status === 401) {
        toast({
          title: "Authentication Error",
          description: "Session expired. Please login again",
          variant: "destructive",
        })
        apiClient.clearAccessToken()
        router.push("/login")
      } else {
        toast({
          title: "Error",
          description: error.message || "Failed to create brand profile",
          variant: "destructive",
        })
      }
    }
  }

  const deleteBrand = async (brandId: number) => {
    if (!confirm("Are you sure you want to delete this brand profile?")) return

    try {
      const token = apiClient.getAccessToken()
      
      if (!token || token === "null" || token === "undefined") {
        toast({
          title: "Authentication Error",
          description: "Please login again",
          variant: "destructive",
        })
        router.push("/login")
        return
      }
      
      await apiClient.deleteBrandProfile(brandId)
      
      toast({
        title: "Success",
        description: "Brand profile deleted successfully",
      })
      fetchBrands()
      
    } catch (error: any) {
      console.error("Error deleting brand:", error)
      
      if (error.status === 401) {
        toast({
          title: "Authentication Error",
          description: "Session expired. Please login again",
          variant: "destructive",
        })
        apiClient.clearAccessToken()
        router.push("/login")
      } else {
        toast({
          title: "Error",
          description: error.message || "Failed to delete brand profile",
          variant: "destructive",
        })
      }
    }
  }

  // Filter and sort brands
  const filteredBrands = brands
    .filter(brand => {
      const matchesSearch = brand.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           brand.description?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesIndustry = filterIndustry === "all" || brand.industry === filterIndustry
      return matchesSearch && matchesIndustry
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "name":
          return a.name.localeCompare(b.name)
        case "industry":
          return a.industry.localeCompare(b.industry)
        case "generations":
          return b.total_generations - a.total_generations
        case "created_at":
        default:
          return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      }
    })

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50/50 dark:bg-gray-950/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-center min-h-[60vh]">
            <div className="text-center space-y-4">
              <div className="w-8 h-8 border-2 border-gray-300 border-t-blue-600 rounded-full animate-spin mx-auto"></div>
              <p className="text-gray-600 dark:text-gray-400">Loading your brands...</p>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-gray-950/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header Section */}
        <div className="mb-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Brand Profiles</h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                Create and manage your brand identities for consistent AI-powered content generation
              </p>
            </div>
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  New Brand
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[600px]">
                <DialogHeader>
                  <DialogTitle className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-blue-100 flex items-center justify-center">
                      <Sparkles className="w-4 h-4 text-blue-600" />
                    </div>
                    Create Brand Profile
                  </DialogTitle>
                  <DialogDescription>
                    Set up a new brand profile to ensure consistent, on-brand content generation.
                  </DialogDescription>
                </DialogHeader>
                <Form {...form}>
                  <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
                    <FormField
                      control={form.control}
                      name="name"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Brand Name</FormLabel>
                          <FormControl>
                            <Input placeholder="Enter brand name" {...field} />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <FormField
                      control={form.control}
                      name="description"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Description</FormLabel>
                          <FormControl>
                            <Textarea
                              placeholder="Describe your brand's mission and values..."
                              className="min-h-[100px]"
                              {...field}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="grid grid-cols-2 gap-4">
                      <FormField
                        control={form.control}
                        name="industry"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Industry</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select industry" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="e-commerce">E-commerce</SelectItem>
                                <SelectItem value="saas">SaaS</SelectItem>
                                <SelectItem value="healthcare">Healthcare</SelectItem>
                                <SelectItem value="finance">Finance</SelectItem>
                                <SelectItem value="education">Education</SelectItem>
                                <SelectItem value="real-estate">Real Estate</SelectItem>
                                <SelectItem value="retail">Retail</SelectItem>
                                <SelectItem value="hospitality">Hospitality</SelectItem>
                                <SelectItem value="technology">Technology</SelectItem>
                                <SelectItem value="fashion">Fashion</SelectItem>
                                <SelectItem value="food">Food & Beverage</SelectItem>
                                <SelectItem value="automotive">Automotive</SelectItem>
                                <SelectItem value="other">Other</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                      
                      <FormField
                        control={form.control}
                        name="visual_style"
                        render={({ field }) => (
                          <FormItem>
                            <FormLabel>Visual Style</FormLabel>
                            <Select onValueChange={field.onChange} defaultValue={field.value}>
                              <FormControl>
                                <SelectTrigger>
                                  <SelectValue placeholder="Select style" />
                                </SelectTrigger>
                              </FormControl>
                              <SelectContent>
                                <SelectItem value="modern">Modern</SelectItem>
                                <SelectItem value="classic">Classic</SelectItem>
                                <SelectItem value="bold">Bold</SelectItem>
                                <SelectItem value="playful">Playful</SelectItem>
                                <SelectItem value="professional">Professional</SelectItem>
                                <SelectItem value="minimal">Minimal</SelectItem>
                                <SelectItem value="luxury">Luxury</SelectItem>
                              </SelectContent>
                            </Select>
                            <FormMessage />
                          </FormItem>
                        )}
                      />
                    </div>
                    
                    <FormField
                      control={form.control}
                      name="brand_keywords"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel>Brand Keywords</FormLabel>
                          <FormControl>
                            <Input
                              placeholder="innovative, trustworthy, modern, sustainable"
                              {...field}
                            />
                          </FormControl>
                          <FormDescription>
                            Comma-separated keywords that describe your brand
                          </FormDescription>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                    
                    <div className="flex justify-end gap-3 pt-4">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setCreateDialogOpen(false)}
                      >
                        Cancel
                      </Button>
                      <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                        <Sparkles className="w-4 h-4 mr-2" />
                        Create Brand
                      </Button>
                    </div>
                  </form>
                </Form>
              </DialogContent>
            </Dialog>
          </div>

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <Card className="bg-white dark:bg-gray-900 border-0 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Brands</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">{brands.length}</p>
                  </div>
                  <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg flex items-center justify-center">
                    <Building2 className="w-6 h-6 text-blue-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white dark:bg-gray-900 border-0 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Total Generations</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {brands.reduce((acc, brand) => acc + brand.total_generations, 0)}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/20 rounded-lg flex items-center justify-center">
                    <Sparkles className="w-6 h-6 text-purple-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white dark:bg-gray-900 border-0 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Campaigns</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {brands.reduce((acc, brand) => acc + brand.successful_campaigns, 0)}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg flex items-center justify-center">
                    <TrendingUp className="w-6 h-6 text-green-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-white dark:bg-gray-900 border-0 shadow-sm">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Active Today</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {brands.filter(brand => 
                        new Date(brand.created_at).toDateString() === new Date().toDateString()
                      ).length}
                    </p>
                  </div>
                  <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900/20 rounded-lg flex items-center justify-center">
                    <Star className="w-6 h-6 text-orange-600" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Filters and Search */}
          <div className="flex flex-col sm:flex-row gap-4 mt-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input
                placeholder="Search brands..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-800"
              />
            </div>
            <Select value={filterIndustry} onValueChange={setFilterIndustry}>
              <SelectTrigger className="w-full sm:w-48 bg-white dark:bg-gray-900">
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Filter by industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                <SelectItem value="e-commerce">E-commerce</SelectItem>
                <SelectItem value="saas">SaaS</SelectItem>
                <SelectItem value="healthcare">Healthcare</SelectItem>
                <SelectItem value="finance">Finance</SelectItem>
                <SelectItem value="education">Education</SelectItem>
                <SelectItem value="technology">Technology</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger className="w-full sm:w-48 bg-white dark:bg-gray-900">
                <SortDesc className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="created_at">Recent</SelectItem>
                <SelectItem value="name">Name</SelectItem>
                <SelectItem value="industry">Industry</SelectItem>
                <SelectItem value="generations">Generations</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Brands Grid */}
        {filteredBrands.length === 0 ? (
          <Card className="bg-white dark:bg-gray-900 border-0 shadow-sm">
            <CardContent className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mb-4">
                <Sparkles className="w-8 h-8 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                {brands.length === 0 ? "No brands yet" : "No brands match your search"}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6 max-w-md">
                {brands.length === 0 
                  ? "Create your first brand profile to start generating consistent, on-brand content."
                  : "Try adjusting your search terms or filters to find what you're looking for."
                }
              </p>
              {brands.length === 0 && (
                <Button 
                  onClick={() => setCreateDialogOpen(true)}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Brand
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredBrands.map((brand) => {
              const industryInfo = industryConfig[brand.industry.toLowerCase() as keyof typeof industryConfig] || industryConfig.other
              const IconComponent = industryInfo.icon
              const styleInfo = brand.visual_style ? visualStyleConfig[brand.visual_style as keyof typeof visualStyleConfig] : null
              
              return (
                <Card key={brand.id} className="bg-white dark:bg-gray-900 border-0 shadow-sm hover:shadow-md transition-all duration-200 group">
                  <CardHeader className="pb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <div className={`w-12 h-12 ${industryInfo.bgColor} rounded-xl flex items-center justify-center flex-shrink-0`}>
                          <IconComponent className="w-6 h-6 text-gray-700 dark:text-gray-300" />
                        </div>
                        <div className="min-w-0 flex-1">
                          <CardTitle className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                            {brand.name}
                          </CardTitle>
                          <div className="flex items-center gap-2 mt-1">
                            <Badge variant="secondary" className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300">
                              {brand.industry.replace("-", " ")}
                            </Badge>
                            {styleInfo && (
                              <Badge variant="outline" className="text-xs">
                                {styleInfo.emoji} {brand.visual_style}
                              </Badge>
                            )}
                          </div>
                        </div>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100 transition-opacity">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => router.push(`/dashboard/brands/${brand.id}`)}>
                            <Eye className="w-4 h-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => router.push(`/dashboard/brands/${brand.id}/edit`)}>
                            <Edit className="w-4 h-4 mr-2" />
                            Edit Brand
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => router.push(`/dashboard/brands/${brand.id}/assets`)}>
                            <Upload className="w-4 h-4 mr-2" />
                            Manage Assets
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => deleteBrand(brand.id)}
                            className="text-red-600 focus:text-red-600"
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete Brand
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {brand.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400 line-clamp-2 leading-relaxed">
                        {brand.description}
                      </p>
                    )}
                    
                    {brand.primary_colors && brand.primary_colors.length > 0 && (
                      <div className="space-y-2">
                        <span className="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                          Brand Colors
                        </span>
                        <div className="flex gap-1.5">
                          {brand.primary_colors.slice(0, 5).map((color, index) => (
                            <div
                              key={index}
                              className="w-6 h-6 rounded-md border border-gray-200 dark:border-gray-700"
                              style={{ backgroundColor: color }}
                              title={color}
                            />
                          ))}
                          {brand.primary_colors.length > 5 && (
                            <div className="w-6 h-6 rounded-md border border-gray-200 dark:border-gray-700 bg-gray-100 dark:bg-gray-800 flex items-center justify-center">
                              <span className="text-xs text-gray-500 font-medium">+{brand.primary_colors.length - 5}</span>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-2 gap-3">
                      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-gray-900 dark:text-white">{brand.total_generations}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Generated</div>
                      </div>
                      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-3 text-center">
                        <div className="text-lg font-bold text-gray-900 dark:text-white">{brand.successful_campaigns}</div>
                        <div className="text-xs text-gray-600 dark:text-gray-400">Campaigns</div>
                      </div>
                    </div>
                    
                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => router.push(`/dashboard/brands/${brand.id}/assets`)}
                      >
                        <Upload className="w-4 h-4 mr-2" />
                        Assets
                      </Button>
                      <Button
                        size="sm"
                        className="flex-1 bg-blue-600 hover:bg-blue-700"
                        onClick={() => router.push(`/dashboard/generate?brand=${brand.id}`)}
                      >
                        <Sparkles className="w-4 h-4 mr-2" />
                        Generate
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}