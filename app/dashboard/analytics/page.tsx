"use client"

import { useState, useEffect } from "react"
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { TrendingUp, TrendingDown, Target, Users, Eye, MousePointer, Share2, DollarSign } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/components/ui/use-toast"
import { useRouter } from "next/navigation"
import { AuthUtils } from "@/lib/auth-utils"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface BrandProfile {
  id: number
  name: string
  industry: string
}

interface MetricCard {
  title: string
  value: string | number
  change: number
  icon: any
  color: string
}

interface PerformanceData {
  date: string
  impressions: number
  engagements: number
  conversions: number
}

export default function AnalyticsPage() {
  const [brands, setBrands] = useState<BrandProfile[]>([])
  const [selectedBrandId, setSelectedBrandId] = useState<string>("")
  const [timeRange, setTimeRange] = useState("30")
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const { toast } = useToast()
  const router = useRouter()

  // Sample data for charts (replace with real data from API)
  const performanceData: PerformanceData[] = [
    { date: "Mon", impressions: 1200, engagements: 180, conversions: 24 },
    { date: "Tue", impressions: 1400, engagements: 220, conversions: 28 },
    { date: "Wed", impressions: 1100, engagements: 160, conversions: 20 },
    { date: "Thu", impressions: 1600, engagements: 280, conversions: 35 },
    { date: "Fri", impressions: 1800, engagements: 320, conversions: 42 },
    { date: "Sat", impressions: 1500, engagements: 260, conversions: 30 },
    { date: "Sun", impressions: 1300, engagements: 200, conversions: 26 },
  ]

  const platformData = [
    { name: "Instagram", value: 35, color: "#E4405F" },
    { name: "Facebook", value: 25, color: "#1877F2" },
    { name: "LinkedIn", value: 20, color: "#0A66C2" },
    { name: "Twitter", value: 15, color: "#1DA1F2" },
    { name: "Email", value: 5, color: "#EA4335" },
  ]

  const contentTypeData = [
    { type: "Product Showcase", performance: 85, conversions: 45 },
    { type: "Lifestyle", performance: 78, conversions: 38 },
    { type: "Promotional", performance: 92, conversions: 56 },
    { type: "Educational", performance: 65, conversions: 28 },
    { type: "Brand Story", performance: 70, conversions: 32 },
  ]

  useEffect(() => {
    fetchBrands()
  }, [])

  useEffect(() => {
    if (selectedBrandId) {
      fetchAnalytics()
    }
  }, [selectedBrandId, timeRange])

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
        if (data.length > 0) {
          setSelectedBrandId(data[0].id.toString())
        }
      }
    } catch (error) {
      console.error("Error fetching brands:", error)
    }
  }

  const fetchAnalytics = async () => {
    if (!selectedBrandId) return

    setLoading(true)
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
      
      const response = await fetch(
        `${API_URL}/analytics/brand/${selectedBrandId}?days=${timeRange}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      )

      if (response.status === 401) {
        AuthUtils.clearAuth()
        router.push("/login")
        return
      }

      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch analytics data",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching analytics:", error)
      toast({
        title: "Error",
        description: "Failed to connect to server",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const metricCards: MetricCard[] = [
    {
      title: "Total Impressions",
      value: analytics?.summary?.total_impressions || 0,
      change: 12.5,
      icon: Eye,
      color: "text-blue-600",
    },
    {
      title: "Engagements",
      value: analytics?.summary?.total_engagements || 0,
      change: 8.2,
      icon: MousePointer,
      color: "text-green-600",
    },
    {
      title: "Conversions",
      value: analytics?.summary?.total_conversions || 0,
      change: -2.4,
      icon: Target,
      color: "text-purple-600",
    },
    {
      title: "Conversion Rate",
      value: `${analytics?.summary?.avg_conversion_rate || 0}%`,
      change: 5.1,
      icon: TrendingUp,
      color: "text-orange-600",
    },
  ]

  return (
    <div className="container mx-auto py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Performance Analytics</h1>
        <p className="text-muted-foreground mt-2">
          Track and analyze your brand content performance
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <Select value={selectedBrandId} onValueChange={setSelectedBrandId}>
          <SelectTrigger className="w-full sm:w-[250px]">
            <SelectValue placeholder="Select a brand" />
          </SelectTrigger>
          <SelectContent>
            {brands.map((brand) => (
              <SelectItem key={brand.id} value={brand.id.toString()}>
                {brand.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger className="w-full sm:w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="7">Last 7 days</SelectItem>
            <SelectItem value="30">Last 30 days</SelectItem>
            <SelectItem value="90">Last 90 days</SelectItem>
            <SelectItem value="365">Last year</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {loading ? (
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      ) : (
        <>
          {/* Metric Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            {metricCards.map((metric, index) => (
              <Card key={index}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">
                    {metric.title}
                  </CardTitle>
                  <metric.icon className={`h-4 w-4 ${metric.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metric.value}</div>
                  <p className="text-xs text-muted-foreground">
                    <span className={metric.change > 0 ? "text-green-600" : "text-red-600"}>
                      {metric.change > 0 ? "+" : ""}{metric.change}%
                    </span>
                    {" "}from last period
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>

          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="content">Content Performance</TabsTrigger>
              <TabsTrigger value="platforms">Platform Analysis</TabsTrigger>
              <TabsTrigger value="campaigns">Campaigns</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <Card>
                  <CardHeader>
                    <CardTitle>Performance Trend</CardTitle>
                    <CardDescription>
                      Daily metrics over the selected period
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={performanceData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line
                          type="monotone"
                          dataKey="impressions"
                          stroke="#3b82f6"
                          strokeWidth={2}
                        />
                        <Line
                          type="monotone"
                          dataKey="engagements"
                          stroke="#10b981"
                          strokeWidth={2}
                        />
                        <Line
                          type="monotone"
                          dataKey="conversions"
                          stroke="#8b5cf6"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Platform Distribution</CardTitle>
                    <CardDescription>
                      Performance breakdown by platform
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={platformData}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          {platformData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>

              {analytics?.conversion_funnel && (
                <Card>
                  <CardHeader>
                    <CardTitle>Conversion Funnel</CardTitle>
                    <CardDescription>
                      User journey from impression to conversion
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">Impressions</span>
                          <span className="text-sm text-muted-foreground">
                            {analytics.conversion_funnel.impression}
                          </span>
                        </div>
                        <Progress value={100} />
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">Engagements</span>
                          <span className="text-sm text-muted-foreground">
                            {analytics.conversion_funnel.engagement} ({analytics.conversion_funnel.engagement_rate}%)
                          </span>
                        </div>
                        <Progress value={analytics.conversion_funnel.engagement_rate} />
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">Click-throughs</span>
                          <span className="text-sm text-muted-foreground">
                            {analytics.conversion_funnel.click_through} ({analytics.conversion_funnel.ctr}%)
                          </span>
                        </div>
                        <Progress value={analytics.conversion_funnel.ctr} />
                      </div>
                      <div>
                        <div className="flex justify-between mb-2">
                          <span className="text-sm font-medium">Conversions</span>
                          <span className="text-sm text-muted-foreground">
                            {analytics.conversion_funnel.conversion} ({analytics.conversion_funnel.conversion_rate}%)
                          </span>
                        </div>
                        <Progress value={analytics.conversion_funnel.conversion_rate} />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="content" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Content Type Performance</CardTitle>
                  <CardDescription>
                    Comparing performance across different content types
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={contentTypeData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="type" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="performance" fill="#3b82f6" name="Performance Score" />
                      <Bar dataKey="conversions" fill="#10b981" name="Conversions" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              {analytics?.top_performing_content && (
                <Card>
                  <CardHeader>
                    <CardTitle>Top Performing Content</CardTitle>
                    <CardDescription>
                      Your best performing generated images
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {analytics.top_performing_content.map((content: any, index: number) => (
                        <div key={index} className="flex items-center space-x-4 p-4 border rounded-lg">
                          <img
                            src={content.image_url}
                            alt={content.prompt}
                            className="w-16 h-16 rounded object-cover"
                          />
                          <div className="flex-1">
                            <p className="text-sm font-medium line-clamp-1">{content.prompt}</p>
                            <div className="flex items-center space-x-4 mt-1 text-xs text-muted-foreground">
                              <span className="flex items-center">
                                <Eye className="h-3 w-3 mr-1" />
                                {content.impressions}
                              </span>
                              <span className="flex items-center">
                                <MousePointer className="h-3 w-3 mr-1" />
                                {content.engagement_rate}%
                              </span>
                              <span className="flex items-center">
                                <Target className="h-3 w-3 mr-1" />
                                {content.conversion_rate}%
                              </span>
                            </div>
                          </div>
                          <Badge variant="secondary">
                            Score: {content.performance_score}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="platforms" className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {Object.entries(analytics?.performance_by_platform || {}).map(([platform, data]: [string, any]) => (
                  <Card key={platform}>
                    <CardHeader>
                      <CardTitle className="text-lg capitalize">{platform}</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Impressions</span>
                          <span className="font-medium">{data.impression || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Engagement</span>
                          <span className="font-medium">{data.engagement || 0}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-sm text-muted-foreground">Conversions</span>
                          <span className="font-medium">{data.conversion || 0}</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </TabsContent>

            <TabsContent value="campaigns" className="space-y-4">
              <Card>
                <CardHeader>
                  <CardTitle>Campaign Performance</CardTitle>
                  <CardDescription>
                    Track the success of your marketing campaigns
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-8 text-muted-foreground">
                    Campaign analytics coming soon
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {analytics?.recommendations && analytics.recommendations.length > 0 && (
            <Card className="mt-8">
              <CardHeader>
                <CardTitle>AI Recommendations</CardTitle>
                <CardDescription>
                  Data-driven suggestions to improve your performance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {analytics.recommendations.map((recommendation: string, index: number) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                        <span className="text-xs font-semibold">{index + 1}</span>
                      </div>
                      <p className="text-sm">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  )
}