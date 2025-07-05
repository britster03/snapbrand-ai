from sqlalchemy import Column, String, DateTime, Text, Boolean, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class Template(Base):
    """Template model for storing image generation templates."""
    
    __tablename__ = "templates"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    # Template content
    prompt_template = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    
    # Default parameters
    default_size = Column(String, default="1024x1024")
    default_guidance_scale = Column(String, default="7.5")
    parameters = Column(Text, nullable=True)  # JSON string for template parameters
    
    # Status
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    generated_images = relationship("GeneratedImage", back_populates="template")
    
    def __repr__(self):
        return f"<Template(id={self.id}, name={self.name}, category={self.category})>" 