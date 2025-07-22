import os
from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    database_url: str = "postgresql://username:password@localhost:5432/mitra_ai"
    async_database_url: str = "postgresql+asyncpg://username:password@localhost:5432/mitra_ai"
    
    # Security
    secret_key: str = "your-super-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Face Recognition
    face_recognition_tolerance: float = 0.6
    max_face_encodings_per_user: int = 5
    
    # Voice Recognition
    voice_recognition_timeout: int = 5
    voice_phrase_time_limit: int = 10
    voice_confidence_threshold: float = 0.7
    
    # System Commands
    allowed_system_commands: List[str] = [
        "ls", "pwd", "whoami", "date", "uptime", "df", "free", "top",
        "ps", "netstat", "uname", "hostname", "id", "groups"
    ]
    max_command_length: int = 100
    
    # Application
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    host: str = "0.0.0.0"
    port: int = 8000
    
    # File Upload
    max_file_size: int = 10485760  # 10MB
    upload_dir: str = "./uploads"
    faces_dir: str = "./uploads/faces"
    audio_dir: str = "./uploads/audio"
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/app.log"

    @field_validator('cors_origins', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v.startswith('['):
            # Handle string representation of list
            import ast
            return ast.literal_eval(v)
        elif isinstance(v, str):
            return [v]
        return v

    @field_validator('allowed_system_commands', mode='before')
    @classmethod
    def assemble_allowed_commands(cls, v):
        if isinstance(v, str) and v.startswith('['):
            import ast
            return ast.literal_eval(v)
        elif isinstance(v, str):
            return [v]
        return v

    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching"""
    return Settings()


# Create required directories
def create_directories():
    """Create required directories if they don't exist"""
    settings = get_settings()
    directories = [
        settings.upload_dir,
        settings.faces_dir,
        settings.audio_dir,
        os.path.dirname(settings.log_file)
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
