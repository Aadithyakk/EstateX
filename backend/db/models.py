from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .session import Base
import enum


class RoleEnum(str, enum.Enum):
    admin = "admin"
    user = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.user)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class KYCStatus(Base):
    __tablename__ = "kyc_status"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String, nullable=False)
    provider_ref = Column(String, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    xrpl_address = Column(String, nullable=False)
    custody_type = Column(String, nullable=False)


class Property(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True, index=True)
    town = Column(String, nullable=True)
    flat_type = Column(String, nullable=True)
    block = Column(String, nullable=True)
    street_name = Column(String, nullable=True)
    storey_range = Column(String, nullable=True)
    floor_area_sqm = Column(Float, nullable=True)
    flat_model = Column(String, nullable=True)
    lease_commence_date = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Valuation(Base):
    __tablename__ = "valuations"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    model_version = Column(String, nullable=True)
    predicted_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    features_json = Column(JSON, nullable=True)
    explanation_json = Column(JSON, nullable=True)


class OfferingStatus(str, enum.Enum):
    draft = "draft"
    live = "live"
    closed = "closed"


class Offering(Base):
    __tablename__ = "offerings"
    id = Column(Integer, primary_key=True, index=True)
    property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
    issuer_address = Column(String, nullable=False)
    currency_code = Column(String, nullable=False)
    total_supply = Column(Float, nullable=False)
    status = Column(Enum(OfferingStatus), default=OfferingStatus.draft)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    offering_id = Column(Integer, ForeignKey("offerings.id"), nullable=False)
    side = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(String, nullable=False)
    xrpl_tx_hash = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
