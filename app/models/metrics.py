from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from sqlalchemy.sql import func
from app.database import Base


class EvalMetrics(Base):
    __tablename__ = "eval_metrics"
    
    # TimescaleDB hypertable columns
    time = Column(DateTime(timezone=True), primary_key=True, server_default=func.now())
    project_id = Column(Integer, nullable=False)
    metric_name = Column(String(100), nullable=False)
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<EvalMetrics(time={self.time}, project_id={self.project_id}, metric='{self.metric_name}', value={self.value})>"


class TraceMetrics(Base):
    __tablename__ = "trace_metrics"
    
    # TimescaleDB hypertable columns
    time = Column(DateTime(timezone=True), primary_key=True, server_default=func.now())
    project_id = Column(Integer, nullable=False)
    model = Column(String(255), nullable=False)
    latency_ms = Column(Float, nullable=False)
    cost_usd = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<TraceMetrics(time={self.time}, project_id={self.project_id}, model='{self.model}', latency={self.latency_ms}ms)>"


class UsageMetrics(Base):
    __tablename__ = "usage_metrics"
    
    # TimescaleDB hypertable columns
    time = Column(DateTime(timezone=True), primary_key=True, server_default=func.now())
    organization_id = Column(Integer, nullable=False)
    api_calls = Column(Integer, nullable=False)
    tokens_used = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"<UsageMetrics(time={self.time}, organization_id={self.organization_id}, api_calls={self.api_calls}, tokens={self.tokens_used})>" 