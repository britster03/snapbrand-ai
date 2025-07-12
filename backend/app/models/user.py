from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """User model for authentication and user management."""
    
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_premium = Column(Boolean, default=False)
    api_key = Column(String, unique=True, nullable=True)
    
    # Usage tracking
    total_images_generated = Column(Integer, default=0)
    total_cost_spent = Column(String, default="0.00")  # Store as string for precision
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    generated_images = relationship("GeneratedImage", back_populates="user", cascade="all, delete-orphan")
    batch_jobs = relationship("BatchJob", back_populates="user", cascade="all, delete-orphan")
    brand_profiles = relationship("BrandProfile", back_populates="user", cascade="all, delete-orphan")
    campaigns = relationship("Campaign", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>" 