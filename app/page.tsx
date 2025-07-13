import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  ArrowRight,
  Sparkles,
  Zap,
  Target,
  Globe,
  Palette,
  Camera,
  Download,
  BarChart3,
  CheckCircle,
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              imagifyy.ai
            </span>
          </div>
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-gray-600 hover:text-gray-900 transition-colors">
              Features
            </Link>
            <Link href="#pricing" className="text-gray-600 hover:text-gray-900 transition-colors">
              Pricing
            </Link>
            <Link href="#api" className="text-gray-600 hover:text-gray-900 transition-colors">
              API
            </Link>
            <Link href="/dashboard" className="text-gray-600 hover:text-gray-900 transition-colors">
              Dashboard
            </Link>
          </nav>
          <div className="flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/dashboard">
                Get Started <ArrowRight className="w-4 h-4 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-6xl">
          <Badge variant="secondary" className="mb-6 bg-blue-100 text-blue-700 border-blue-200">
            <Sparkles className="w-4 h-4 mr-2" />
            AI-Powered Brand Asset Studio
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent leading-tight">
            Generate On-Brand
            <br />
            Visuals at Scale
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed">
            Transform your brand guidelines into unlimited, professional-quality images. No photographer or designer
            needed—just your vision and our AI.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Button size="lg" className="text-lg px-8 py-6" asChild>
              <Link href="/dashboard">
                Start Creating Free <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 py-6 bg-transparent">
              Watch Demo <Camera className="w-5 h-5 ml-2" />
            </Button>
          </div>

          {/* Hero Image */}
          <div className="relative max-w-5xl mx-auto">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-1">
              <div className="bg-white rounded-xl p-8">
                <Image
                  src="/placeholder.svg?height=600&width=1000"
                  alt="imagifyy.ai Dashboard Preview"
                  width={1000}
                  height={600}
                  className="rounded-lg shadow-2xl"
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Everything You Need for Brand Consistency</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              From brand asset ingestion to bulk generation, we've built every tool you need to scale your visual
              content.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <Card className="border-2 hover:border-blue-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <Palette className="w-12 h-12 text-blue-600 mb-4" />
                <CardTitle>Brand Asset Ingestion</CardTitle>
                <CardDescription>
                  Upload logos, color palettes, and sample photos. Our AI learns your exact brand style.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-purple-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <Target className="w-12 h-12 text-purple-600 mb-4" />
                <CardTitle>Template-Based Prompting</CardTitle>
                <CardDescription>
                  Pre-built templates for product shots, lifestyle scenes, social media, and more.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-green-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <Globe className="w-12 h-12 text-green-600 mb-4" />
                <CardTitle>Real-Time Context</CardTitle>
                <CardDescription>
                  Images adapt to weather, events, and holidays for timely, relevant campaigns.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-orange-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <Zap className="w-12 h-12 text-orange-600 mb-4" />
                <CardTitle>Batch Generation</CardTitle>
                <CardDescription>
                  Generate hundreds of variants instantly. Perfect for product catalogs and campaigns.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-red-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <BarChart3 className="w-12 h-12 text-red-600 mb-4" />
                <CardTitle>Developer API</CardTitle>
                <CardDescription>
                  REST API for automation. Integrate with Shopify, WooCommerce, and your existing tools.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-2 hover:border-indigo-200 transition-colors" variant="gradient" animateHover>
              <CardHeader>
                <Download className="w-12 h-12 text-indigo-600 mb-4" />
                <CardTitle>Export & Edit</CardTitle>
                <CardDescription>
                  Fine-tune with sliders, export high-res images, and get auto-generated alt-text.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto max-w-6xl">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div>
              <div className="text-4xl font-bold mb-2">10K+</div>
              <div className="text-blue-100">Images Generated</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">500+</div>
              <div className="text-blue-100">Happy Brands</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">95%</div>
              <div className="text-blue-100">Time Saved</div>
            </div>
            <div>
              <div className="text-4xl font-bold mb-2">24/7</div>
              <div className="text-blue-100">AI Availability</div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">Simple, Transparent Pricing</h2>
            <p className="text-xl text-gray-600">Choose the plan that fits your brand's needs</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <Card className="border-2">
              <CardHeader>
                <CardTitle>Starter</CardTitle>
                <CardDescription>Perfect for small businesses</CardDescription>
                <div className="text-3xl font-bold">
                  $29<span className="text-lg text-gray-500">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    100 images/month
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Basic templates
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Brand asset upload
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    HD downloads
                  </li>
                </ul>
                <Button className="w-full mt-6">Get Started</Button>
              </CardContent>
            </Card>

            <Card className="border-2 border-blue-500 relative">
              <Badge className="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-blue-500">Most Popular</Badge>
              <CardHeader>
                <CardTitle>Professional</CardTitle>
                <CardDescription>For growing brands</CardDescription>
                <div className="text-3xl font-bold">
                  $99<span className="text-lg text-gray-500">/month</span>
                </div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    500 images/month
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    All templates
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Batch generation
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    API access
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Priority support
                  </li>
                </ul>
                <Button className="w-full mt-6">Get Started</Button>
              </CardContent>
            </Card>

            <Card className="border-2">
              <CardHeader>
                <CardTitle>Enterprise</CardTitle>
                <CardDescription>For large organizations</CardDescription>
                <div className="text-3xl font-bold">Custom</div>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Unlimited images
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Custom templates
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    White-label option
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    Dedicated support
                  </li>
                  <li className="flex items-center">
                    <CheckCircle className="w-5 h-5 text-green-500 mr-2" />
                    SLA guarantee
                  </li>
                </ul>
                <Button variant="outline" className="w-full mt-6 bg-transparent">
                  Contact Sales
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gray-900 text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Brand Visuals?</h2>
          <p className="text-xl text-gray-300 mb-8">
            Join hundreds of brands already creating stunning, on-brand content with imagifyy.ai
          </p>
          <Button size="lg" className="text-lg px-8 py-6 bg-blue-600 hover:bg-blue-700" asChild>
            <Link href="/dashboard">
              Start Your Free Trial <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
