from sqlalchemy import Column, String, Text, DateTime, Enum
from sqlalchemy.sql import func
from ..database import Base
import enum

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, enum.Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    department = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    assignee_id = Column(String, nullable=True)
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), default=TicketPriority.NORMAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution = Column(Text, nullable=True)