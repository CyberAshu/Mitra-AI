from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID
import re


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v


class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, v):
        if v and len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime]
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


# Face Recognition Schemas
class FaceEncodingBase(BaseModel):
    encoding_name: str
    confidence_score: Optional[float] = 0.0
    is_primary: Optional[bool] = False


class FaceEncodingCreate(FaceEncodingBase):
    pass


class FaceEncodingResponse(FaceEncodingBase):
    id: UUID
    user_id: UUID
    image_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Voice Recognition Schemas
class VoiceProfileBase(BaseModel):
    profile_name: str
    wake_phrase: Optional[str] = None
    confidence_threshold: Optional[float] = 0.7
    is_active: Optional[bool] = True


class VoiceProfileCreate(VoiceProfileBase):
    pass


class VoiceProfileResponse(VoiceProfileBase):
    id: UUID
    user_id: UUID
    audio_file_path: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Command History Schemas
class CommandHistoryBase(BaseModel):
    command: str
    command_type: str
    execution_status: Optional[str] = "pending"
    output: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None

    @field_validator('command_type')
    def validate_command_type(cls, v):
        allowed_types = ['voice', 'face', 'manual', 'system']
        if v not in allowed_types:
            raise ValueError(f'Command type must be one of: {allowed_types}')
        return v

    @field_validator('execution_status')
    def validate_execution_status(cls, v):
        if v:
            allowed_statuses = ['pending', 'running', 'success', 'failed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'Execution status must be one of: {allowed_statuses}')
        return v


class CommandHistoryCreate(CommandHistoryBase):
    pass


class CommandHistoryResponse(CommandHistoryBase):
    id: UUID
    user_id: UUID
    executed_at: datetime

    class Config:
        from_attributes = True


# Authentication Schemas
class AuthSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    auth_method: str
    ip_address: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: datetime
    last_accessed: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse


class TokenData(BaseModel):
    username: Optional[str] = None


# Face Authentication Schemas
class FaceAuthRequest(BaseModel):
    image_data: str  # Base64 encoded image
    tolerance: Optional[float] = None


class FaceAuthResponse(BaseModel):
    success: bool
    user_id: Optional[UUID] = None
    confidence: Optional[float] = None
    message: str
    token: Optional[Token] = None


# Voice Authentication Schemas
class VoiceAuthRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    expected_phrase: Optional[str] = None
    timeout: Optional[int] = 5


class VoiceAuthResponse(BaseModel):
    success: bool
    user_id: Optional[UUID] = None
    recognized_text: Optional[str] = None
    confidence: Optional[float] = None
    message: str
    token: Optional[Token] = None


# System Command Schemas
class SystemCommandRequest(BaseModel):
    command: str
    args: Optional[List[str]] = []
    timeout: Optional[int] = 30

    @field_validator('command')
    def validate_command(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Command cannot be empty')
        if len(v) > 1000:
            raise ValueError('Command too long')
        return v.strip()


class SystemCommandResponse(BaseModel):
    success: bool
    command: str
    output: Optional[str] = None
    error: Optional[str] = None
    execution_time: float
    exit_code: Optional[int] = None
