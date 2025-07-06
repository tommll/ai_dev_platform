from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Input and output
    input_data = Column(JSON, nullable=False)
    expected_output = Column(Text)
    actual_output = Column(Text)
    
    # Metrics
    accuracy_score = Column(Float)
    latency_ms = Column(Float)
    cost_usd = Column(Float)
    custom_metrics = Column(JSON)  # Additional evaluation metrics
    
    # Status
    is_success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Foreign keys
    experiment_run_id = Column(Integer, ForeignKey("experiment_runs.id"), nullable=False)
    dataset_item_id = Column(Integer, ForeignKey("dataset_items.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    experiment_run = relationship("ExperimentRun", back_populates="evaluation_results")
    dataset_item = relationship("DatasetItem")
    
    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, experiment_run_id={self.experiment_run_id}, accuracy={self.accuracy_score})>" 