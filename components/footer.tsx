import * as React from "react"
import { cn } from "@/lib/utils"
import { Sparkles, Twitter, Facebook, Instagram, Linkedin } from "lucide-react"
import Link from "next/link"

const Footer: React.FC<{ className?: string }> = ({ className }) => {
  return (
    <footer className={cn("bg-gradient-to-r from-blue-600 to-purple-600 text-white py-12", className)} role="contentinfo">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="col-span-1 md:col-span-2">
            <Link href="/" className="inline-flex items-center space-x-2 mb-4" aria-label="SnapBrand.ai Home">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-blue-600" aria-hidden="true" />
              </div>
              <span className="text-xl font-bold text-white">SnapBrand.ai</span>
            </Link>
            <p className="text-blue-100 mb-4 max-w-md">AI-powered brand asset studio to generate on-brand visuals at scale.</p>
            <nav className="flex space-x-4" aria-label="Social Media Links">
              <a href="https://twitter.com" className="text-blue-100 hover:text-white transition-colors" aria-label="Twitter">
                <Twitter className="w-5 h-5" aria-hidden="true" />
              </a>
              <a href="https://facebook.com" className="text-blue-100 hover:text-white transition-colors" aria-label="Facebook">
                <Facebook className="w-5 h-5" aria-hidden="true" />
              </a>
              <a href="https://instagram.com" className="text-blue-100 hover:text-white transition-colors" aria-label="Instagram">
                <Instagram className="w-5 h-5" aria-hidden="true" />
              </a>
              <a href="https://linkedin.com" className="text-blue-100 hover:text-white transition-colors" aria-label="LinkedIn">
                <Linkedin className="w-5 h-5" aria-hidden="true" />
              </a>
            </nav>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Product</h3>
            <nav aria-label="Product Navigation">
              <ul className="space-y-2">
                <li><Link href="#features" className="text-blue-100 hover:text-white transition-colors">Features</Link></li>
                <li><Link href="#pricing" className="text-blue-100 hover:text-white transition-colors">Pricing</Link></li>
                <li><Link href="#api" className="text-blue-100 hover:text-white transition-colors">API</Link></li>
                <li><Link href="/dashboard" className="text-blue-100 hover:text-white transition-colors">Dashboard</Link></li>
              </ul>
            </nav>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-4">Support</h3>
            <nav aria-label="Support Navigation">
              <ul className="space-y-2">
                <li><Link href="/contact" className="text-blue-100 hover:text-white transition-colors">Contact Us</Link></li>
                <li><Link href="/terms" className="text-blue-100 hover:text-white transition-colors">Terms of Service</Link></li>
                <li><Link href="/privacy" className="text-blue-100 hover:text-white transition-colors">Privacy Policy</Link></li>
              </ul>
            </nav>
          </div>
        </div>
        <div className="mt-12 pt-8 border-t border-blue-500/30 text-center text-blue-100 text-sm">
          <p>© {new Date().getFullYear()} SnapBrand.ai. All rights reserved.</p>
        </div>
      </div>
    </footer>
  )
}

Footer.displayName = "Footer"

export { Footer } 