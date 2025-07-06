from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Trace(Base):
    __tablename__ = "traces"
    
    id = Column(Integer, primary_key=True, index=True)
    trace_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Request/Response data
    prompt_id = Column(Integer, ForeignKey("prompts.id"), nullable=False)
    input_data = Column(JSON, nullable=False)
    output_data = Column(JSON)
    
    # Performance metrics
    latency_ms = Column(Float)
    tokens_used = Column(Integer)
    cost_usd = Column(Float)
    
    # Model information
    model_name = Column(String(255))
    model_provider = Column(String(100))
    
    # Status
    is_success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Foreign keys
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project")
    prompt = relationship("Prompt")
    
    def __repr__(self):
        return f"<Trace(id={self.id}, trace_id='{self.trace_id}', latency={self.latency_ms}ms)>" 