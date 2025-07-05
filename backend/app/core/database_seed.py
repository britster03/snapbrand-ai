import json
from sqlalchemy.orm import Session
from ..models.database import SessionLocal
from ..models.template import Template
from ..models.user import User
from ..core.auth import get_password_hash, generate_api_key

def seed_templates(db: Session):
    """Seed the database with predefined templates."""
    
    templates_data = [
        {
            "id": "product-hero",
            "name": "Product Hero Shot",
            "category": "E-commerce",
            "description": "Professional product photography with clean background",
            "prompt_template": "Professional product photography of {product_name}, {style_description}, clean white background, studio lighting, high resolution, commercial photography",
            "negative_prompt": "blurry, low quality, watermark, text overlay, cluttered background",
            "default_size": "1024x1024",
            "parameters": json.dumps({
                "style_description": "modern minimalist design",
                "lighting": "studio lighting",
                "background": "clean white"
            })
        },
        {
            "id": "instagram-post",
            "name": "Instagram Post",
            "category": "Social Media",
            "description": "Square format optimized for Instagram feed",
            "prompt_template": "Instagram-worthy image of {subject}, {mood} atmosphere, {style} style, perfect for social media, square composition",
            "negative_prompt": "text overlay, watermark, low quality, blurry",
            "default_size": "1080x1080",
            "parameters": json.dumps({
                "mood": "bright and cheerful",
                "style": "modern",
                "composition": "square"
            })
        },
        {
            "id": "lifestyle-scene",
            "name": "Lifestyle Scene",
            "category": "Marketing",
            "description": "Authentic lifestyle photography showing products in use",
            "prompt_template": "Lifestyle photography of {subject} in {setting}, {mood} atmosphere, natural lighting, authentic, relatable scene",
            "negative_prompt": "staged, artificial, overly perfect, stock photo look",
            "default_size": "1024x1024",
            "parameters": json.dumps({
                "setting": "modern home environment",
                "mood": "warm and inviting",
                "lighting": "natural"
            })
        },
        {
            "id": "email-header",
            "name": "Email Header",
            "category": "Marketing",
            "description": "Wide format header image for email campaigns",
            "prompt_template": "Email header design featuring {subject}, {brand_style} aesthetic, {color_scheme} color palette, professional marketing image",
            "negative_prompt": "text overlay, cluttered, low resolution",
            "default_size": "1200x400",
            "parameters": json.dumps({
                "brand_style": "modern and professional",
                "color_scheme": "brand colors",
                "format": "wide header"
            })
        },
        {
            "id": "website-banner",
            "name": "Website Banner",
            "category": "Web",
            "description": "Hero banner for website homepage",
            "prompt_template": "Website hero banner featuring {subject}, {brand_style} design, {color_scheme}, modern web design aesthetic",
            "negative_prompt": "text, buttons, navigation elements, low quality",
            "default_size": "1920x600",
            "parameters": json.dumps({
                "brand_style": "clean and modern",
                "color_scheme": "brand palette",
                "format": "wide banner"
            })
        }
    ]
    
    for template_data in templates_data:
        # Check if template already exists
        existing = db.query(Template).filter(Template.id == template_data["id"]).first()
        if not existing:
            template = Template(**template_data)
            db.add(template)
            print(f"Added template: {template_data['name']}")
    
    db.commit()
    print("Templates seeded successfully!")


def create_test_user(db: Session):
    """Create a test user for development."""
    
    # Check if test user already exists
    existing_user = db.query(User).filter(User.email == "test@snapbrand.ai").first()
    if existing_user:
        print("Test user already exists")
        return existing_user
    
    # Create test user
    test_user = User(
        id="user_test001",
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
    
    print(f"Test user created: {test_user.email}")
    print(f"Password: password123")
    print(f"API Key: {test_user.api_key}")
    
    return test_user


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    
    try:
        print("Seeding database...")
        seed_templates(db)
        create_test_user(db)
        print("Database seeding completed!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database() 