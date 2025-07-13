#!/usr/bin/env python3
"""
Comprehensive test setup script for SnapBrand.ai
Creates test brand, user, and provides sample prompts for testing all features.
"""

import sys
import os
sys.path.append('.')

from app.models.database import SessionLocal, init_db
from app.models.user import User
from app.models.brand import BrandProfile
from app.models.template import Template
from app.core.auth import get_password_hash, generate_api_key
from sqlalchemy.exc import IntegrityError
import json

def create_test_user(db):
    """Create or get test user."""
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == "test@snapbrand.ai") | (User.username == "testuser")
        ).first()
        
        if existing_user:
            print(f"✓ Test user already exists: {existing_user.email}")
            return existing_user
        
        # Create new test user
        test_user = User(
            id="user_test_001",
            email="test@snapbrand.ai",
            username="testuser",
            hashed_password=get_password_hash("password123"),
            full_name="Test User",
            is_active=True,
            is_premium=True,
            api_key=generate_api_key()
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✓ Test user created: {test_user.email}")
        print(f"  Password: password123")
        print(f"  API Key: {test_user.api_key}")
        
        return test_user
        
    except IntegrityError as e:
        db.rollback()
        print(f"⚠ User creation failed (likely exists): {e}")
        # Try to get existing user
        return db.query(User).filter(User.email == "test@snapbrand.ai").first()

def create_test_brand(db, user):
    """Create a comprehensive test brand profile."""
    try:
        # Check if brand exists
        existing_brand = db.query(BrandProfile).filter(
            BrandProfile.name == "SnapBrand Test Company"
        ).first()
        
        if existing_brand:
            print(f"✓ Test brand already exists: {existing_brand.name}")
            return existing_brand
        
        # Import the Industry enum
        from app.models.brand import Industry
        
        # Create comprehensive test brand
        test_brand = BrandProfile(
            user_id=user.id,
            name="SnapBrand Test Company",
            description="A innovative tech company focused on AI-powered solutions for modern businesses. We create cutting-edge software that helps companies streamline their operations and boost productivity.",
            industry=Industry.TECHNOLOGY,
            brand_values=["innovation", "reliability", "user-centric", "efficiency", "transparency"],
            target_audience={
                "primary": {
                    "age_range": "25-45",
                    "demographics": ["business professionals", "entrepreneurs", "tech enthusiasts"],
                    "interests": ["technology", "productivity", "innovation", "business growth"],
                    "pain_points": ["inefficient processes", "outdated tools", "complex software"]
                },
                "secondary": {
                    "age_range": "30-55",
                    "demographics": ["executives", "decision makers"],
                    "interests": ["ROI", "scalability", "competitive advantage"]
                }
            },
            competitors=["Microsoft", "Google Workspace", "Slack", "Notion", "Asana"],
            unique_selling_points=[
                "AI-powered automation",
                "Intuitive user interface", 
                "Seamless integrations",
                "24/7 customer support",
                "Enterprise-grade security"
            ],
            primary_colors=["#2563EB", "#7C3AED", "#059669"],  # Blue, Purple, Green
            secondary_colors=["#F59E0B", "#EF4444", "#6B7280"],  # Orange, Red, Gray
            font_families={
                "primary": "Inter",
                "secondary": "Roboto",
                "accent": "Poppins"
            },
            logo_style="modern minimalist",
            visual_style="clean, professional, modern",
            preferred_image_styles=[
                "clean and minimalist",
                "professional photography",
                "modern illustrations",
                "geometric patterns",
                "gradient backgrounds"
            ],
            avoided_elements=[
                "cluttered layouts",
                "outdated design elements", 
                "overly complex graphics",
                "dark or gloomy themes",
                "cartoon-style illustrations"
            ],
            brand_keywords=[
                "innovation", "technology", "AI", "automation", "efficiency",
                "modern", "professional", "reliable", "scalable", "intuitive"
            ]
        )
        
        db.add(test_brand)
        db.commit()
        db.refresh(test_brand)
        
        print(f"✓ Test brand created: {test_brand.name}")
        print(f"  Industry: {test_brand.industry.value}")
        print(f"  Colors: {test_brand.primary_colors}")
        print(f"  Style: {test_brand.visual_style}")
        
        return test_brand
        
    except IntegrityError as e:
        db.rollback()
        print(f"⚠ Brand creation failed: {e}")
        return None
    except Exception as e:
        db.rollback()
        print(f"⚠ Brand creation failed: {e}")
        return None

def print_test_prompts():
    """Print comprehensive test prompts for all features."""
    
    print("\n" + "="*80)
    print("🎨 COMPREHENSIVE TEST PROMPTS FOR SNAPBRAND.AI")
    print("="*80)
    
    print("\n📸 1. PRODUCT PHOTOGRAPHY PROMPTS:")
    print("   • Professional product shot of a sleek smartphone on a clean white background")
    print("   • Modern laptop computer in a minimalist office setting with soft lighting")
    print("   • Elegant smartwatch displayed on a marble surface with professional lighting")
    print("   • High-end headphones on a gradient background, studio photography style")
    
    print("\n🏢 2. CORPORATE/BUSINESS PROMPTS:")
    print("   • Professional business team meeting in a modern conference room")
    print("   • Diverse group of professionals collaborating around a whiteboard")
    print("   • Modern office space with natural lighting and contemporary furniture")
    print("   • Executive presenting data visualization on a large screen")
    
    print("\n🎯 3. MARKETING & ADVERTISING PROMPTS:")
    print("   • Dynamic hero banner for a tech company website, modern and professional")
    print("   • Social media post design featuring innovation and technology themes")
    print("   • Email newsletter header with clean, corporate aesthetic")
    print("   • Landing page hero image showcasing AI and automation concepts")
    
    print("\n🎨 4. BRAND ILLUSTRATION PROMPTS:")
    print("   • Abstract geometric illustration representing innovation and growth")
    print("   • Modern isometric illustration of a digital workspace")
    print("   • Minimalist icon set for a productivity software application")
    print("   • Corporate infographic elements in a clean, professional style")
    
    print("\n🌟 5. LIFESTYLE & CONCEPT PROMPTS:")
    print("   • Professional using cutting-edge technology in a modern workspace")
    print("   • Successful entrepreneur working on a laptop in a contemporary office")
    print("   • Team celebrating a successful project launch in a modern office")
    print("   • Innovation concept with futuristic technology elements")
    
    print("\n🎭 6. CREATIVE & ARTISTIC PROMPTS:")
    print("   • Abstract representation of AI and machine learning concepts")
    print("   • Futuristic data visualization with flowing geometric patterns")
    print("   • Modern art piece representing digital transformation")
    print("   • Creative interpretation of cloud computing and connectivity")
    
    print("\n🏭 7. INDUSTRY-SPECIFIC PROMPTS:")
    print("   • Fintech: Secure digital banking interface on mobile device")
    print("   • Healthcare: Modern medical technology in a clean hospital setting")
    print("   • Education: Interactive learning environment with digital tools")
    print("   • E-commerce: Streamlined online shopping experience visualization")
    
    print("\n⚙️ 8. TECHNICAL & UI PROMPTS:")
    print("   • Clean dashboard interface showing analytics and data insights")
    print("   • Modern mobile app interface with intuitive navigation")
    print("   • Sophisticated software interface with professional design")
    print("   • API integration visualization with clean, technical aesthetic")

def print_test_scenarios():
    """Print test scenarios for different features."""
    
    print("\n" + "="*80)
    print("🧪 FEATURE TESTING SCENARIOS")
    print("="*80)
    
    print("\n🎯 1. BRAND-AWARE GENERATION:")
    print("   Test: Use any prompt above with the 'SnapBrand Test Company' brand selected")
    print("   Expected: Images should incorporate blue/purple color scheme and modern style")
    
    print("\n📦 2. BATCH GENERATION:")
    print("   Test: Create 3-5 requests with different prompts from above")
    print("   Expected: All images generated efficiently in batch mode")
    
    print("\n🎨 3. VECTOR GENERATION:")
    print("   Test: 'Modern logo for tech company' with 'modern' style")
    print("   Expected: Scalable SVG logo matching brand guidelines")
    
    print("\n📊 4. QUALITY LEVELS:")
    print("   Test: Same prompt with different quality settings (standard, high, ultra, professional)")
    print("   Expected: Noticeable quality improvements at higher levels")
    
    print("\n🎭 5. STYLE VARIATIONS:")
    print("   Test: Same prompt with different styles (photorealistic, artistic, technical)")
    print("   Expected: Distinct visual styles while maintaining brand consistency")
    
    print("\n💾 6. TEMPLATE USAGE:")
    print("   Test: Select 'Product Hero Shot' template and use product prompts")
    print("   Expected: Professional product photography style applied")

def print_login_info():
    """Print login information."""
    
    print("\n" + "="*80)
    print("🔐 LOGIN INFORMATION")
    print("="*80)
    print("Email: test@snapbrand.ai")
    print("Password: password123")
    print("Brand: SnapBrand Test Company")
    print("\n💡 TIP: The brand is pre-configured with professional colors and style guidelines!")

def main():
    """Main setup function."""
    print("🚀 Setting up SnapBrand.ai test environment...")
    
    # Initialize database
    init_db()
    print("✓ Database initialized")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create test user
        user = create_test_user(db)
        if not user:
            print("❌ Failed to create test user")
            return
        
        # Create test brand
        brand = create_test_brand(db, user)
        if not brand:
            print("❌ Failed to create test brand")
            return
        
        print("\n✅ Test environment setup complete!")
        
        # Print all test information
        print_login_info()
        print_test_prompts()
        print_test_scenarios()
        
        print("\n" + "="*80)
        print("🎉 READY TO TEST! Visit http://localhost:3000 and start generating!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 