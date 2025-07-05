"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Copy, Book, Zap, Shield, Globe, Check, Eye, EyeOff, Plus, Trash2, RefreshCw } from "lucide-react"
import Link from "next/link"

export default function APIPage() {
  const [showApiKey, setShowApiKey] = useState(false)
  const [copiedCode, setCopiedCode] = useState<string | null>(null)

  const apiKeys = [
    {
      id: 1,
      name: "Production API Key",
      key: "sb_live_1234567890abcdef",
      created: "2024-01-15",
      lastUsed: "2 hours ago",
      requests: 15420,
      status: "active",
    },
    {
      id: 2,
      name: "Development API Key",
      key: "sb_test_abcdef1234567890",
      created: "2024-01-10",
      lastUsed: "1 day ago",
      requests: 892,
      status: "active",
    },
  ]

  const endpoints = [
    {
      method: "POST",
      path: "/api/v1/generate",
      description: "Generate a single image",
      rateLimit: "100/hour",
    },
    {
      method: "POST",
      path: "/api/v1/batch",
      description: "Start a batch generation job",
      rateLimit: "10/hour",
    },
    {
      method: "GET",
      path: "/api/v1/batch/{id}",
      description: "Get batch job status",
      rateLimit: "1000/hour",
    },
    {
      method: "GET",
      path: "/api/v1/images",
      description: "List generated images",
      rateLimit: "500/hour",
    },
    {
      method: "GET",
      path: "/api/v1/templates",
      description: "List available templates",
      rateLimit: "100/hour",
    },
  ]

  const codeExamples = {
    curl: `curl -X POST https://api.snapbrand.ai/v1/generate \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "template": "product-hero",
    "prompt": "A modern smartphone on white background",
    "style_intensity": 75,
    "high_resolution": true
  }'`,
    javascript: `const response = await fetch('https://api.snapbrand.ai/v1/generate', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_API_KEY',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    template: 'product-hero',
    prompt: 'A modern smartphone on white background',
    style_intensity: 75,
    high_resolution: true
  })
});

const result = await response.json();
console.log(result);`,
    python: `import requests

url = "https://api.snapbrand.ai/v1/generate"
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json"
}
data = {
    "template": "product-hero",
    "prompt": "A modern smartphone on white background",
    "style_intensity": 75,
    "high_resolution": True
}

response = requests.post(url, headers=headers, json=data)
result = response.json()
print(result)`,
    php: `<?php
$url = 'https://api.snapbrand.ai/v1/generate';
$headers = [
    'Authorization: Bearer YOUR_API_KEY',
    'Content-Type: application/json'
];
$data = [
    'template' => 'product-hero',
    'prompt' => 'A modern smartphone on white background',
    'style_intensity' => 75,
    'high_resolution' => true
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

$result = json_decode($response, true);
print_r($result);
?>`,
  }

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text)
    setCopiedCode(type)
    setTimeout(() => setCopiedCode(null), 2000)
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
            <h1 className="text-xl font-semibold">API Documentation</h1>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant="secondary" className="bg-blue-100 text-blue-700">
              API v1.0
            </Badge>
            <Button variant="outline" size="sm">
              <Book className="w-4 h-4 mr-2" />
              Full Docs
            </Button>
          </div>
        </div>
      </header>

      <div className="p-6">
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="keys">API Keys</TabsTrigger>
            <TabsTrigger value="endpoints">Endpoints</TabsTrigger>
            <TabsTrigger value="examples">Code Examples</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">API Requests</CardTitle>
                  <Zap className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">16,312</div>
                  <p className="text-xs text-muted-foreground">+8% from last month</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
                  <Shield className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">99.2%</div>
                  <p className="text-xs text-muted-foreground">+0.3% improvement</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Avg Response</CardTitle>
                  <Globe className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2.3s</div>
                  <p className="text-xs text-muted-foreground">-0.2s faster</p>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Getting Started</CardTitle>
                <CardDescription>Quick start guide for the SnapBrand.ai API</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h3 className="font-semibold">1. Get your API Key</h3>
                  <p className="text-sm text-gray-600">
                    Generate an API key from the API Keys tab to authenticate your requests.
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold">2. Make your first request</h3>
                  <p className="text-sm text-gray-600">
                    Use our REST API to generate images programmatically. All requests require authentication.
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold">3. Handle responses</h3>
                  <p className="text-sm text-gray-600">
                    Our API returns JSON responses with image URLs, metadata, and status information.
                  </p>
                </div>
                <div className="space-y-2">
                  <h3 className="font-semibold">4. Monitor usage</h3>
                  <p className="text-sm text-gray-600">
                    Track your API usage, rate limits, and performance metrics in this dashboard.
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Base URL</CardTitle>
                <CardDescription>All API requests should be made to this base URL</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between p-3 bg-gray-100 rounded-lg">
                  <code className="text-sm">https://api.snapbrand.ai/v1</code>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard("https://api.snapbrand.ai/v1", "base-url")}
                  >
                    {copiedCode === "base-url" ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="keys" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold">API Keys</h2>
                <p className="text-gray-600">Manage your API keys for authentication</p>
              </div>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Create New Key
              </Button>
            </div>

            <div className="space-y-4">
              {apiKeys.map((key) => (
                <Card key={key.id}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <h3 className="font-semibold">{key.name}</h3>
                        <p className="text-sm text-gray-500">
                          Created {key.created} • Last used {key.lastUsed}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className="bg-green-100 text-green-700">{key.status}</Badge>
                        <Button variant="outline" size="sm">
                          <RefreshCw className="w-4 h-4 mr-1" />
                          Regenerate
                        </Button>
                        <Button variant="outline" size="sm">
                          <Trash2 className="w-4 h-4 mr-1" />
                          Delete
                        </Button>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2 mb-4">
                      <div className="flex-1 p-3 bg-gray-100 rounded-lg font-mono text-sm">
                        {showApiKey ? key.key : "••••••••••••••••••••••••••••••••"}
                      </div>
                      <Button variant="outline" size="sm" onClick={() => setShowApiKey(!showApiKey)}>
                        {showApiKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                      <Button variant="outline" size="sm" onClick={() => copyToClipboard(key.key, `key-${key.id}`)}>
                        {copiedCode === `key-${key.id}` ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </Button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">{key.requests.toLocaleString()}</div>
                        <div className="text-xs text-gray-500">Total Requests</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">100/hour</div>
                        <div className="text-xs text-gray-500">Rate Limit</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded">
                        <div className="text-lg font-semibold">Active</div>
                        <div className="text-xs text-gray-500">Status</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="endpoints" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">API Endpoints</h2>
              <p className="text-gray-600">Available endpoints and their usage</p>
            </div>

            <div className="space-y-4">
              {endpoints.map((endpoint, index) => (
                <Card key={index}>
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-3">
                        <Badge variant={endpoint.method === "GET" ? "secondary" : "default"}>{endpoint.method}</Badge>
                        <code className="text-sm bg-gray-100 px-2 py-1 rounded">{endpoint.path}</code>
                      </div>
                      <Badge variant="outline">{endpoint.rateLimit}</Badge>
                    </div>
                    <p className="text-gray-600">{endpoint.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Authentication</CardTitle>
                <CardDescription>All API requests require authentication</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">Include your API key in the Authorization header:</p>
                  <div className="flex items-center justify-between p-3 bg-gray-100 rounded-lg">
                    <code className="text-sm">Authorization: Bearer YOUR_API_KEY</code>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard("Authorization: Bearer YOUR_API_KEY", "auth-header")}
                    >
                      {copiedCode === "auth-header" ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="examples" className="space-y-6">
            <div>
              <h2 className="text-2xl font-bold mb-2">Code Examples</h2>
              <p className="text-gray-600">Example requests in different programming languages</p>
            </div>

            <Tabs defaultValue="curl" className="w-full">
              <TabsList>
                <TabsTrigger value="curl">cURL</TabsTrigger>
                <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                <TabsTrigger value="python">Python</TabsTrigger>
                <TabsTrigger value="php">PHP</TabsTrigger>
              </TabsList>

              {Object.entries(codeExamples).map(([lang, code]) => (
                <TabsContent key={lang} value={lang}>
                  <Card>
                    <CardHeader className="flex flex-row items-center justify-between">
                      <CardTitle className="capitalize">{lang} Example</CardTitle>
                      <Button variant="outline" size="sm" onClick={() => copyToClipboard(code, lang)}>
                        {copiedCode === lang ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                        Copy
                      </Button>
                    </CardHeader>
                    <CardContent>
                      <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                        <code>{code}</code>
                      </pre>
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}
            </Tabs>

            <Card>
              <CardHeader>
                <CardTitle>Response Format</CardTitle>
                <CardDescription>Example API response</CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`{
  "id": "img_1234567890",
  "status": "completed",
  "url": "https://cdn.snapbrand.ai/images/generated/img_1234567890.png",
  "thumbnail_url": "https://cdn.snapbrand.ai/images/thumbnails/img_1234567890.jpg",
  "metadata": {
    "template": "product-hero",
    "prompt": "A modern smartphone on white background",
    "dimensions": {
      "width": 1024,
      "height": 1024
    },
    "format": "png",
    "file_size": 245760,
    "created_at": "2024-01-15T10:30:00Z"
  },
  "credits_used": 1
}`}</code>
                </pre>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
