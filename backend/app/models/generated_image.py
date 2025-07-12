from sqlalchemy import Column, String, DateTime, Float, Integer, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class GeneratedImage(Base):
    """Generated image model for storing image generation results."""
    
    __tablename__ = "generated_images"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Image details
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    size = Column(String, nullable=False)
    
    # Storage details
    s3_url = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    
    # Generation parameters
    guidance_scale = Column(Float, nullable=True)
    seed = Column(Integer, nullable=True)
    template_id = Column(String, ForeignKey("templates.id"), nullable=True)
    
    # Brand and campaign associations
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Batch information
    batch_id = Column(String, ForeignKey("batch_jobs.id"), nullable=True)
    batch_index = Column(Integer, nullable=True)
    
    # Cost tracking
    generation_cost = Column(String, default="0.00")  # Store as string for precision
    
    # Metadata
    brand_style = Column(Text, nullable=True)  # JSON string
    processing_time = Column(Float, nullable=True)
    
    # Status
    is_public = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="generated_images")
    template = relationship("Template", back_populates="generated_images")
    batch_job = relationship("BatchJob", back_populates="generated_images")
    brand_profile = relationship("BrandProfile")
    campaign = relationship("Campaign", back_populates="generated_images")
    performance_metrics = relationship("PerformanceMetric", back_populates="generated_image", cascade="all, delete-orphan")
    approval_workflow = relationship("ApprovalWorkflow", back_populates="generated_image", uselist=False)
    
    def __repr__(self):
        return f"<GeneratedImage(id={self.id}, user_id={self.user_id}, prompt={self.prompt[:50]}...)>" 