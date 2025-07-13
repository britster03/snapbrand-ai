"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
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
  Upload,
  Wand2,
  Layers,
  RefreshCw,
  MessageSquare,
  Play,
  Users,
  Clock,
  TrendingUp,
  Star,
  Code,
  Cpu,
  Shield,
  Workflow,
  Image as ImageIcon,
  FileImage,
  Paintbrush,
  Settings,
  Database,
  CloudUpload,
  Gauge,
  Brain,
  Lightbulb,
  Rocket,
  Award,
  ChevronRight,
  ExternalLink,
  Menu,
  X,
  Heart
} from "lucide-react"
import Link from "next/link"
import Image from "next/image"
import { useState } from "react"

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-blue-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50 transition-all duration-300">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                SnapBrand.ai
              </span>
              <div className="text-xs text-gray-500 font-medium">Professional AI Image Generation</div>
            </div>
          </div>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="#features" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
              Features
            </Link>
            <Link href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
              How It Works
            </Link>
            <Link href="#demo-showcase" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
              See It In Action
            </Link>
          </nav>
          
          <div className="flex items-center space-x-4">
            <Button variant="ghost" className="hidden md:flex hover:bg-blue-50 transition-colors duration-300" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </Button>
          </div>
        </div>
        
        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t bg-white/95 backdrop-blur-sm">
            <nav className="container mx-auto px-4 py-4 flex flex-col space-y-4">
              <Link href="#features" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
                Features
              </Link>
              <Link href="#how-it-works" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
                How It Works
              </Link>
              <Link href="#demo-showcase" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
                See It In Action
              </Link>
              <Separator />
              <Link href="/login" className="text-gray-600 hover:text-blue-600 transition-colors duration-300 font-medium">
                Sign In
              </Link>
            </nav>
          </div>
        )}
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-blue-50/50 to-purple-50/50 -z-10"></div>
        <div className="container mx-auto text-center max-w-6xl">
          <div className="max-w-4xl mx-auto mb-16">
            <Badge variant="secondary" className="mb-6 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 border-blue-200 hover:scale-105 transition-transform duration-300">
              <Sparkles className="w-4 h-4 mr-2" />
              Professional AI Image Generation Platform
            </Badge>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-8 bg-gradient-to-r from-gray-900 via-blue-800 to-purple-800 bg-clip-text text-transparent leading-tight animate-in fade-in-50 slide-in-from-bottom-10 duration-1000">
              Generate Professional
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Brand-Consistent
              </span>
              <br />
              Visuals at Scale
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto leading-relaxed animate-in fade-in-50 slide-in-from-bottom-10 duration-1000 delay-200">
              Transform your brand assets into unlimited, professional-quality images using Amazon Titan V2 AI. 
              Built for production with industry-standard quality controls and transparent pricing.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12 animate-in fade-in-50 slide-in-from-bottom-10 duration-1000 delay-400">
              <Button 
                size="lg" 
                variant="outline" 
                className="text-lg px-8 py-6 border-2 border-blue-200 hover:bg-blue-50 hover:border-blue-300 transition-all duration-300 hover:scale-105 group"
              >
                <Camera className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300" />
                View Examples
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Demo Showcase Section */}
      <section id="demo-showcase" className="py-20 px-4 bg-gradient-to-br from-gray-50 to-blue-50/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-6 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 border-blue-200">
              <Camera className="w-4 h-4 mr-2" />
              See It In Action
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-blue-800 bg-clip-text text-transparent">
              Professional Results
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Watch how SnapBrand.ai transforms your brand assets into stunning, professional-quality images
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* Demo Placeholder 1 - Video/Image Support */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden hover:shadow-3xl transition-all duration-500">
                <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {/* Placeholder for video/image - Replace with your content */}
                  <div className="text-center space-y-2">
                    <Play className="w-12 h-12 text-gray-400 mx-auto" />
                    <p className="text-sm text-gray-500">Video/Image Placeholder 1</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Demo Placeholder 2 - Video/Image Support */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/20 to-blue-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden hover:shadow-3xl transition-all duration-500">
                <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {/* Placeholder for video/image - Replace with your content */}
                  <div className="text-center space-y-2">
                    <Play className="w-12 h-12 text-gray-400 mx-auto" />
                    <p className="text-sm text-gray-500">Video/Image Placeholder 2</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Demo Placeholder 3 - Video/Image Support */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden hover:shadow-3xl transition-all duration-500">
                <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {/* Placeholder for video/image - Replace with your content */}
                  <div className="text-center space-y-2">
                    <Play className="w-12 h-12 text-gray-400 mx-auto" />
                    <p className="text-sm text-gray-500">Video/Image Placeholder 3</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Demo Placeholder 4 - Video/Image Support */}
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-2xl blur-xl group-hover:blur-2xl transition-all duration-300"></div>
              <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-200 overflow-hidden hover:shadow-3xl transition-all duration-500">
                <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {/* Placeholder for video/image - Replace with your content */}
                  <div className="text-center space-y-2">
                    <Play className="w-12 h-12 text-gray-400 mx-auto" />
                    <p className="text-sm text-gray-500">Video/Image Placeholder 4</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-6 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 border-blue-200">
              <Star className="w-4 h-4 mr-2" />
              Production-Ready Features
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-blue-800 bg-clip-text text-transparent">
              Everything You Need for
              <br />
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Professional Image Generation
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              Built with industry-standard features and AWS infrastructure for reliable, scalable image generation
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Amazon Titan V2 */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-blue-50 to-blue-100/50 hover:from-blue-100 hover:to-blue-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <Cpu className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-blue-700 transition-colors duration-300">
                  Amazon Titan V2
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  Latest generation AI model with superior prompt adherence and professional-grade quality output
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm text-blue-600 font-medium group-hover:text-blue-700 transition-colors duration-300">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Enterprise-grade AI model
                </div>
              </CardContent>
            </Card>

            {/* Vector Generation */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-purple-50 to-purple-100/50 hover:from-purple-100 hover:to-purple-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                  <FileImage className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-purple-700 transition-colors duration-300">
                  Vector Generation
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  Create scalable SVG graphics with multiple styles: Modern, Minimalist, Artistic, Geometric
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm text-purple-600 font-medium group-hover:text-purple-700 transition-colors duration-300">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Scalable vector graphics
                </div>
              </CardContent>
            </Card>

            {/* Quality Controls */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-amber-50 to-amber-100/50 hover:from-amber-100 hover:to-amber-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg" style={{background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)'}}>
                  <Shield className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-amber-700 transition-colors duration-300">
                  Quality Controls
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  4 quality levels with automated validation: Standard, High, Ultra, Professional
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm font-medium group-hover:text-amber-700 transition-colors duration-300" style={{color: '#f59e0b'}}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Automated quality validation
                </div>
              </CardContent>
            </Card>

            {/* Brand Management */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-orange-50 to-orange-100/50 hover:from-orange-100 hover:to-orange-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg" style={{background: 'linear-gradient(135deg, #ea580c 0%, #c2410c 100%)'}}>
                  <Palette className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-orange-700 transition-colors duration-300">
                  Brand Management
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  Upload brand assets, manage color palettes, and maintain consistent visual identity
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm font-medium group-hover:text-orange-700 transition-colors duration-300" style={{color: '#ea580c'}}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Consistent brand identity
                </div>
              </CardContent>
            </Card>

            {/* Batch Processing */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-emerald-50 to-emerald-100/50 hover:from-emerald-100 hover:to-emerald-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg" style={{background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)'}}>
                  <Layers className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-emerald-700 transition-colors duration-300">
                  Batch Processing
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  Generate multiple images efficiently with batch jobs and real-time progress tracking
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm font-medium group-hover:text-emerald-700 transition-colors duration-300" style={{color: '#10b981'}}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Efficient bulk generation
                </div>
              </CardContent>
            </Card>

            {/* AWS Infrastructure */}
            <Card className="group hover:shadow-2xl transition-all duration-500 hover:-translate-y-2 border-0 bg-gradient-to-br from-slate-50 to-slate-100/50 hover:from-slate-100 hover:to-slate-200/50">
              <CardHeader className="pb-4">
                <div className="w-16 h-16 rounded-2xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300 shadow-lg" style={{background: 'linear-gradient(135deg, #475569 0%, #334155 100%)'}}>
                  <CloudUpload className="w-8 h-8 text-white" />
                </div>
                <CardTitle className="text-xl font-bold text-gray-900 group-hover:text-slate-700 transition-colors duration-300">
                  AWS Infrastructure
                </CardTitle>
                <CardDescription className="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
                  Bedrock AI, S3 Storage, IAM Security - enterprise-grade infrastructure
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center text-sm font-medium group-hover:text-slate-700 transition-colors duration-300" style={{color: '#475569'}}>
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Enterprise-grade security
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="py-20 px-4 bg-gradient-to-br from-gray-50 to-blue-50/30">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <Badge variant="secondary" className="mb-6 bg-gradient-to-r from-blue-100 to-purple-100 text-blue-700 border-blue-200">
              <Workflow className="w-4 h-4 mr-2" />
              Simple Process
            </Badge>
            <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-gray-900 to-blue-800 bg-clip-text text-transparent">
              How SnapBrand.ai Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
              From brand asset upload to professional image generation—here's how our AI transforms your brand into unlimited visual content
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Step 1 */}
            <div className="text-center group">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-3xl flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                  <Upload className="w-10 h-10 text-white" />
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-blue-700 transition-colors duration-300">
                Upload Brand Assets
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Start by uploading your brand essentials: logos, color palettes, typography samples, and reference images that represent your brand style.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center group">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                  <Brain className="w-10 h-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  2
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-purple-700 transition-colors duration-300">
                AI Analyzes Your Brand
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Our advanced AI powered by Amazon Titan V2 analyzes your brand assets to understand your unique style, color preferences, and visual identity.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center group">
              <div className="relative mb-6">
              <div className="w-20 h-20 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-3xl flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                  <Wand2 className="w-10 h-10 text-white drop-shadow-lg" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  3
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-emerald-700 transition-colors duration-300">
                Generate Professional Images
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Watch as AI creates multiple variations of your content in seconds. Fine-tune with our editing tools and choose your preferred quality level.
              </p>
            </div>

            {/* Step 4 */}
            <div className="text-center group">
              <div className="relative mb-6">
                <div className="w-20 h-20 bg-gradient-to-br from-orange-500 to-orange-600 rounded-3xl flex items-center justify-center mx-auto shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
                  <Download className="w-10 h-10 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 w-8 h-8 bg-gradient-to-br from-orange-600 to-red-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  4
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3 group-hover:text-orange-700 transition-colors duration-300">
                Download & Use
              </h3>
              <p className="text-gray-600 leading-relaxed">
                Download high-resolution files ready for immediate use. Perfect for marketing campaigns, social media, or any professional application.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">
            Ready to Transform Your Brand Visuals?
          </h2>
          <p className="text-xl mb-8 text-blue-100">
            Join hundreds of businesses creating professional, on-brand content with AI
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              variant="outline" 
              className="text-lg px-8 py-6 bg-white text-blue-600 hover:bg-blue-50 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-xl"
            >
              <MessageSquare className="w-5 h-5 mr-2" />
              Contact Sales
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <p className="text-sm text-gray-400">
              © 2024 SnapBrand.ai. All rights reserved. Built with <Heart className="w-4 h-4 mx-1 text-red-500 inline" /> for professional image generation.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}
