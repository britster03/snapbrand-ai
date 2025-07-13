# SnapBrand.ai Testing Guide 🚀

## Quick Start

### 🔐 Login Information
- **Email:** `test@snapbrand.ai`
- **Password:** `password123`
- **Test Brand:** `SnapBrand Test Company`

### 🎨 Brand Details
- **Industry:** Technology
- **Colors:** Blue (#2563EB), Purple (#7C3AED), Green (#059669)
- **Style:** Clean, professional, modern
- **Keywords:** innovation, technology, AI, automation, efficiency

---

## 🧪 Test Prompts by Category

### 📸 Product Photography
```
• Professional product shot of a sleek smartphone on a clean white background
• Modern laptop computer in a minimalist office setting with soft lighting
• Elegant smartwatch displayed on a marble surface with professional lighting
• High-end headphones on a gradient background, studio photography style
```

### 🏢 Corporate/Business
```
• Professional business team meeting in a modern conference room
• Diverse group of professionals collaborating around a whiteboard
• Modern office space with natural lighting and contemporary furniture
• Executive presenting data visualization on a large screen
```

### 🎯 Marketing & Advertising
```
• Dynamic hero banner for a tech company website, modern and professional
• Social media post design featuring innovation and technology themes
• Email newsletter header with clean, corporate aesthetic
• Landing page hero image showcasing AI and automation concepts
```

### 🎨 Brand Illustrations
```
• Abstract geometric illustration representing innovation and growth
• Modern isometric illustration of a digital workspace
• Minimalist icon set for a productivity software application
• Corporate infographic elements in a clean, professional style
```

### 🌟 Lifestyle & Concepts
```
• Professional using cutting-edge technology in a modern workspace
• Successful entrepreneur working on a laptop in a contemporary office
• Team celebrating a successful project launch in a modern office
• Innovation concept with futuristic technology elements
```

### 🎭 Creative & Artistic
```
• Abstract representation of AI and machine learning concepts
• Futuristic data visualization with flowing geometric patterns
• Modern art piece representing digital transformation
• Creative interpretation of cloud computing and connectivity
```

---

## 🧪 Feature Testing Scenarios

### 1. 🎯 Brand-Aware Generation
**Test:** Use any prompt above with 'SnapBrand Test Company' brand selected
**Expected:** Images should incorporate blue/purple color scheme and modern style

### 2. 📦 Batch Generation
**Test:** Create 3-5 requests with different prompts from above
**Expected:** All images generated efficiently in batch mode

### 3. 🎨 Vector Generation
**Test:** 'Modern logo for tech company' with 'modern' style
**Expected:** Scalable SVG logo matching brand guidelines

### 4. 📊 Quality Levels
**Test:** Same prompt with different quality settings (standard, high, ultra, professional)
**Expected:** Noticeable quality improvements at higher levels

### 5. 🎭 Style Variations
**Test:** Same prompt with different styles (photorealistic, artistic, technical)
**Expected:** Distinct visual styles while maintaining brand consistency

### 6. 💾 Template Usage
**Test:** Select 'Product Hero Shot' template and use product prompts
**Expected:** Professional product photography style applied

---

## 🔧 Database Management

### If Database Gets Locked
Run the health check script:
```bash
cd backend
python db_health_check.py
```

### Manual Cleanup (if needed)
```bash
# Kill any hanging processes
pkill -f "python.*main.py"

# Remove lock files
rm -f snapbrand.db-journal snapbrand.db-wal snapbrand.db-shm

# Test connection
python -c "import sqlite3; conn = sqlite3.connect('snapbrand.db'); print('OK'); conn.close()"
```

---

## 🚀 Getting Started

1. **Start the backend:**
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend:**
   ```bash
   npm run dev
   ```

3. **Visit:** `http://localhost:3000`

4. **Login** with the test credentials above

5. **Select the test brand** when generating images

6. **Try the test prompts** and explore all features!

---

## 🎉 Features to Test

- ✅ **Beautiful Loading Animation** - Watch the multi-stage progress indicator
- ✅ **Brand-Aware Generation** - Images match your brand colors and style
- ✅ **Batch Processing** - Generate multiple images efficiently
- ✅ **Vector Generation** - Create scalable SVG graphics
- ✅ **Quality Controls** - Test different quality levels
- ✅ **Template System** - Use pre-built templates
- ✅ **Style Variations** - Explore different artistic styles
- ✅ **Brand Management** - Manage brand profiles and guidelines

---

## 💡 Pro Tips

1. **Brand Selection:** Always select "SnapBrand Test Company" for consistent results
2. **Quality Testing:** Try the same prompt with different quality levels
3. **Batch Efficiency:** Use batch generation for multiple variations
4. **Vector Graphics:** Great for logos and scalable graphics
5. **Template Power:** Templates provide professional starting points

---

## 🆘 Troubleshooting

### Database Issues
- Run `python db_health_check.py` to diagnose and fix
- Check for hanging Python processes
- Ensure no multiple backend instances are running

### Generation Issues
- Verify AWS credentials are set
- Check backend logs for errors
- Ensure proper brand selection

### Frontend Issues
- Clear browser cache
- Check console for JavaScript errors
- Verify backend is running on port 8000

---

**Happy Testing! 🎨✨** 