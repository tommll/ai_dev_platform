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
    experiment_run_id = Column(Text, ForeignKey("experiment_runs.id"), nullable=False)
    dataset_item_id = Column(Integer, ForeignKey("dataset_items.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    experiment_run = relationship("ExperimentRun", back_populates="evaluation_results")
    dataset_item = relationship("DatasetItem")
    
    def __repr__(self):
        return (f"<EvaluationResult("
                f"id={self.id}, "
                f"experiment_run_id={self.experiment_run_id}, "
                f"input_data={self.input_data}, "
                f"expected_output={self.expected_output}, "
                f"actual_output={self.actual_output}, "
                f"accuracy={self.accuracy_score}, "
                f"latency={self.latency_ms}, "
                f"cost={self.cost_usd}, "
                f"custom_metrics={self.custom_metrics}, "
                f"is_success={self.is_success}, "
                f"error_message={self.error_message}, "
                f"dataset_item_id={self.dataset_item_id}, "
                f"created_at={self.created_at})>")