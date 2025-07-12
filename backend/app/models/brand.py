from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
import enum


class Industry(enum.Enum):
    ECOMMERCE = "e-commerce"
    SAAS = "saas"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    REALESTATE = "real-estate"
    RETAIL = "retail"
    HOSPITALITY = "hospitality"
    TECHNOLOGY = "technology"
    FASHION = "fashion"
    FOOD = "food"
    AUTOMOTIVE = "automotive"
    OTHER = "other"


class BrandProfile(Base):
    __tablename__ = "brand_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    industry = Column(SQLEnum(Industry), nullable=False, default=Industry.OTHER)
    
    # Brand attributes
    brand_values = Column(JSON)  # List of brand values
    target_audience = Column(JSON)  # Demographics and psychographics
    competitors = Column(JSON)  # List of competitor names
    unique_selling_points = Column(JSON)  # USPs
    
    # Visual identity
    primary_colors = Column(JSON)  # Array of hex colors
    secondary_colors = Column(JSON)  # Array of hex colors
    font_families = Column(JSON)  # Primary and secondary fonts
    logo_style = Column(String(100))  # minimal, bold, playful, professional, etc.
    visual_style = Column(String(100))  # modern, classic, minimalist, etc.
    
    # Style preferences
    preferred_image_styles = Column(JSON)  # photorealistic, illustration, etc.
    avoided_elements = Column(JSON)  # Things to avoid in generated content
    brand_keywords = Column(JSON)  # Keywords that represent the brand
    
    # Performance metrics
    avg_engagement_rate = Column(Float, default=0.0)
    total_generations = Column(Integer, default=0)
    successful_campaigns = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="brand_profiles")
    brand_assets = relationship("BrandAsset", back_populates="brand_profile", cascade="all, delete-orphan")
    brand_guidelines = relationship("BrandGuideline", back_populates="brand_profile", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="brand_profile", cascade="all, delete-orphan")
    performance_metrics = relationship("PerformanceMetric", back_populates="brand_profile", cascade="all, delete-orphan")


class BrandAsset(Base):
    __tablename__ = "brand_assets"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    
    asset_type = Column(String(50), nullable=False)  # logo, image, font, color_palette, etc.
    asset_name = Column(String(255), nullable=False)
    asset_url = Column(String(500), nullable=False)  # S3 URL
    
    # Extracted metadata
    dominant_colors = Column(JSON)  # Extracted color palette
    style_attributes = Column(JSON)  # Detected style attributes
    text_elements = Column(JSON)  # Any text found in the asset
    composition_data = Column(JSON)  # Layout and composition analysis
    
    # Asset properties
    file_size = Column(Integer)  # in bytes
    dimensions = Column(JSON)  # {width, height}
    file_format = Column(String(20))
    
    analysis_completed = Column(Boolean, default=False)
    analysis_data = Column(JSON)  # Complete analysis results
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="brand_assets")


class BrandGuideline(Base):
    __tablename__ = "brand_guidelines"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    
    guideline_type = Column(String(50), nullable=False)  # color, typography, imagery, tone, layout
    rule_name = Column(String(255), nullable=False)
    rule_description = Column(Text)
    
    # Rule specifics
    rule_data = Column(JSON)  # Specific rule parameters
    priority = Column(Integer, default=5)  # 1-10, higher is more important
    is_mandatory = Column(Boolean, default=False)
    
    # Validation
    validation_function = Column(String(100))  # Name of validation function to use
    validation_parameters = Column(JSON)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="brand_guidelines")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(100))  # product_launch, seasonal, awareness, etc.
    
    # Campaign details
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    target_platforms = Column(JSON)  # List of platforms
    target_metrics = Column(JSON)  # KPIs and goals
    
    # Status
    status = Column(String(50), default="draft")  # draft, active, paused, completed
    total_assets_generated = Column(Integer, default=0)
    
    # Performance
    actual_metrics = Column(JSON)  # Actual performance data
    roi = Column(Float)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="campaigns")
    user = relationship("User", back_populates="campaigns")
    generated_images = relationship("GeneratedImage", back_populates="campaign")


class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    generated_image_id = Column(Integer, ForeignKey("generated_images.id"), nullable=True, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True, index=True)
    
    metric_type = Column(String(50), nullable=False)  # engagement, conversion, reach, etc.
    metric_value = Column(Float, nullable=False)
    metric_data = Column(JSON)  # Additional metric details
    
    platform = Column(String(50))  # instagram, facebook, email, etc.
    recorded_at = Column(DateTime, server_default=func.now())
    
    # A/B testing
    variant_id = Column(String(100))  # For A/B test tracking
    is_control = Column(Boolean, default=False)
    
    # Relationships
    brand_profile = relationship("BrandProfile", back_populates="performance_metrics")
    generated_image = relationship("GeneratedImage", back_populates="performance_metrics")
    campaign = relationship("Campaign")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    role = Column(String(50), nullable=False)  # admin, editor, viewer
    permissions = Column(JSON)  # Specific permissions
    
    invited_by = Column(String, ForeignKey("users.id"))
    joined_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    brand_profile = relationship("BrandProfile")
    user = relationship("User", foreign_keys=[user_id])
    invited_by_user = relationship("User", foreign_keys=[invited_by])


class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    brand_profile_id = Column(Integer, ForeignKey("brand_profiles.id"), nullable=False, index=True)
    generated_image_id = Column(String, ForeignKey("generated_images.id"), nullable=False, index=True)
    
    requested_by = Column(String, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected, revision
    
    # Approval chain
    approvers = Column(JSON)  # List of user IDs who need to approve
    current_approver_index = Column(Integer, default=0)
    approval_history = Column(JSON)  # History of approvals/rejections
    
    comments = Column(Text)
    revision_notes = Column(Text)
    
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    brand_profile = relationship("BrandProfile")
    generated_image = relationship("GeneratedImage", back_populates="approval_workflow")
    requester = relationship("User")