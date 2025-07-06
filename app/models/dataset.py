from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="datasets")
    items = relationship("DatasetItem", back_populates="dataset", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}')>"


class DatasetItem(Base):
    __tablename__ = "dataset_items"
    
    id = Column(Integer, primary_key=True, index=True)
    input_data = Column(JSON, nullable=False)  # Input data for the prompt
    expected_output = Column(Text)  # Expected output/answer
    # metadata = Column(JSON)  # Additional metadata
    
    # Foreign keys
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dataset = relationship("Dataset", back_populates="items")
    
    def __repr__(self):
        return f"<DatasetItem(id={self.id}, dataset_id={self.dataset_id})>" 