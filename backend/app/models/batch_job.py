from sqlalchemy import Column, String, DateTime, Integer, Float, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base


class BatchJob(Base):
    """Batch job model for storing batch processing information."""
    
    __tablename__ = "batch_jobs"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    
    # Job details
    status = Column(String, nullable=False, default="queued", index=True)
    priority = Column(String, nullable=False, default="normal")
    
    # Progress tracking
    total_requests = Column(Integer, nullable=False)
    completed_requests = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    progress = Column(Float, default=0.0)
    
    # Cost tracking
    estimated_cost = Column(String, default="0.00")  # Store as string for precision
    actual_cost = Column(String, default="0.00")
    
    # Processing details
    processing_time = Column(Float, nullable=True)
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    
    # Request data
    requests_data = Column(Text, nullable=False)  # JSON string of requests
    
    # Results
    results_data = Column(Text, nullable=True)  # JSON string of results
    error_details = Column(Text, nullable=True)  # JSON string of errors
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="batch_jobs")
    generated_images = relationship("GeneratedImage", back_populates="batch_job")
    
    def __repr__(self):
        return f"<BatchJob(id={self.id}, user_id={self.user_id}, status={self.status}, progress={self.progress}%)>" 