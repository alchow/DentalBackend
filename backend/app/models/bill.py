from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Numeric, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum

from app.db.base_class import Base

class BillStatus(str, enum.Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    INSURANCE_CLAIMED = "INSURANCE_CLAIMED"

# Many-to-Many Association Table
bill_codes_association = Table(
    "bill_codes",
    Base.metadata,
    Column("bill_id", UUID(as_uuid=True), ForeignKey("bills.id"), primary_key=True),
    Column("code_id", String, ForeignKey("cdt_codes.code"), primary_key=True),
)

class CdtCode(Base):
    __tablename__ = "cdt_codes"
    
    code = Column(String, primary_key=True, index=True) # e.g. D0120
    description = Column(String, nullable=False)
    category = Column(String, nullable=True)

class Bill(Base):
    __tablename__ = "bills"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    visit_id = Column(UUID(as_uuid=True), ForeignKey("visits.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BillStatus), default=BillStatus.PENDING, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())

    patient = relationship("Patient", back_populates="bills")
    visit = relationship("Visit", back_populates="bills")
    codes = relationship("CdtCode", secondary=bill_codes_association)
