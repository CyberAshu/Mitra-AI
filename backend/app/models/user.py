from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, LargeBinary, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # Authentication timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Face recognition data
    face_encodings = relationship("FaceEncoding", back_populates="user", cascade="all, delete-orphan")
    
    # Voice recognition data
    voice_profiles = relationship("VoiceProfile", back_populates="user", cascade="all, delete-orphan")
    
    # System commands history
    command_history = relationship("CommandHistory", back_populates="user", cascade="all, delete-orphan")
    
    # Authentication sessions
    auth_sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")


class FaceEncoding(Base):
    __tablename__ = "face_encodings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    encoding_name = Column(String(100), nullable=False)  # e.g., "main", "profile_1", etc.
    encoding_data = Column(LargeBinary, nullable=False)  # Serialized face encoding
    image_path = Column(String(255), nullable=True)  # Path to original image
    confidence_score = Column(Float, default=0.0)
    is_primary = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key relationship
    user = relationship("User", back_populates="face_encodings")


class VoiceProfile(Base):
    __tablename__ = "voice_profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    profile_name = Column(String(100), nullable=False)  # e.g., "wake_word", "command_phrase"
    audio_file_path = Column(String(255), nullable=True)  # Path to audio sample
    voice_features = Column(Text, nullable=True)  # JSON string of voice features
    wake_phrase = Column(String(255), nullable=True)  # Wake phrase for voice activation
    confidence_threshold = Column(Float, default=0.7)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign key relationship
    user = relationship("User", back_populates="voice_profiles")


class CommandHistory(Base):
    __tablename__ = "command_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    command = Column(Text, nullable=False)
    command_type = Column(String(50), nullable=False)  # "voice", "face", "manual"
    execution_status = Column(String(20), default="pending")  # "pending", "success", "failed"
    output = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time = Column(Float, nullable=True)  # Time taken to execute in seconds
    
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign key relationship
    user = relationship("User", back_populates="command_history")


class AuthSession(Base):
    __tablename__ = "auth_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    auth_method = Column(String(50), nullable=False)  # "face", "voice", "password", "combined"
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign key relationship
    user = relationship("User", back_populates="auth_sessions")
