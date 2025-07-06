import type React from "react"
import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"
import { AuthProvider } from '@/components/auth-context'
import { Toaster } from '@/components/ui/toaster'
import { Footer } from '@/components/footer'

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "SnapBrand.ai - AI-Powered Brand Asset Studio",
  description: "Generate on-brand visuals at scale with AI. No photographer or designer needed.",
    generator: 'v0.dev'
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          {children}
          <Footer />
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  )
}
