from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
import logging

from app.core.database import get_async_db
from app.core.config import get_settings
from app.models.user import User, AuthSession, FaceEncoding, VoiceProfile, CommandHistory
from app.schemas.user import UserCreate, UserLogin, Token, UserResponse
import uuid

router = APIRouter()
security = HTTPBearer()
settings = get_settings()
logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> dict:
        """Decode and verify JWT token"""
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )


auth_service = AuthService()


async def load_full_user(db: AsyncSession, user_id: int = None, username: str = None) -> User:
    """Load user with all relationships eagerly to avoid lazy loading issues"""
    stmt = select(User).options(
        selectinload(User.face_encodings),
        selectinload(User.voice_profiles),
        selectinload(User.command_history),
        selectinload(User.auth_sessions)
    )
    
    if user_id is not None:
        stmt = stmt.where(User.id == user_id)
    elif username is not None:
        stmt = stmt.where(User.username == username)
    else:
        raise ValueError("Either user_id or username must be provided")
    
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current authenticated user"""
    token = credentials.credentials
    payload = auth_service.decode_token(token)
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database with all relationships loaded to avoid lazy loading issues
    user = await load_full_user(db, username=username)
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    return user


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user"""
    try:
        # Check if username already exists
        stmt = select(User).where(User.username == user_data.username)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Check if email already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        hashed_password = auth_service.hash_password(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            is_active=True,
            is_superuser=False
        )
        
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        logger.info(f"New user registered: {user_data.username}")
        
        # Convert the user object to dict first to avoid lazy loading issues
        user_dict = {
            "id": db_user.id,
            "username": db_user.username,
            "email": db_user.email,
            "full_name": db_user.full_name,
            "is_active": db_user.is_active,
            "is_superuser": db_user.is_superuser,
            "created_at": db_user.created_at,
            "updated_at": db_user.updated_at,
            "last_login": db_user.last_login
        }
        
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user and return access token"""
    try:
        # Get user from database with all relationships loaded
        user = await load_full_user(db, username=user_credentials.username)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Verify password
        if not auth_service.verify_password(user_credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = auth_service.create_access_token(
            data={"sub": user.username, "user_id": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Create auth session
        auth_session = AuthSession(
            user_id=user.id,
            session_token=access_token,
            auth_method="password",
            expires_at=datetime.utcnow() + access_token_expires,
            is_active=True
        )
        
        db.add(auth_session)
        
        # Update last login
        current_time = datetime.utcnow()
        user.last_login = current_time
        await db.commit()
        await db.refresh(user)  # Ensure the user object is refreshed after commit
        
        logger.info(f"User logged in: {user.username}")
        
        # Create UserResponse object immediately while in async context
        user_response = UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_superuser=user.is_superuser,
            created_at=user.created_at,
            updated_at=user.updated_at,
            last_login=user.last_login
        )
        
        # Create and return Token with the pre-created user_response
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """Logout user and invalidate token"""
    try:
        token = credentials.credentials
        
        # Deactivate auth session
        stmt = select(AuthSession).where(
            AuthSession.session_token == token,
            AuthSession.is_active == True
        )
        result = await db.execute(stmt)
        auth_session = result.scalar_one_or_none()
        
        if auth_session:
            auth_session.is_active = False
            await db.commit()
        
        logger.info(f"User logged out: {current_user.username}")
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get current user information"""
    # Load full user with all relationships to avoid lazy loading issues
    user = await load_full_user(db, user_id=current_user.id)
    
    # Convert the user object to dict first to avoid lazy loading issues
    user_dict = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login
    }
    
    return UserResponse(**user_dict)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update current user information"""
    try:
        # Update allowed fields
        allowed_fields = ['full_name', 'email']
        
        for field, value in user_update.items():
            if field in allowed_fields and hasattr(current_user, field):
                setattr(current_user, field, value)
        
        # Handle password change
        if 'password' in user_update:
            new_password = user_update['password']
            if len(new_password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must be at least 8 characters long"
                )
            current_user.hashed_password = auth_service.hash_password(new_password)
        
        current_user.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"User updated: {current_user.username}")
        
        # Convert the user object to dict first to avoid lazy loading issues
        user_dict = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "is_active": current_user.is_active,
            "is_superuser": current_user.is_superuser,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at,
            "last_login": current_user.last_login
        }
        
        return UserResponse(**user_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Update failed"
        )


@router.get("/sessions")
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user's active sessions"""
    try:
        stmt = select(AuthSession).where(
            AuthSession.user_id == current_user.id,
            AuthSession.is_active == True
        ).order_by(AuthSession.created_at.desc())
        
        result = await db.execute(stmt)
        sessions = result.scalars().all()
        
        return [
            {
                "id": str(session.id),
                "auth_method": session.auth_method,
                "created_at": session.created_at,
                "expires_at": session.expires_at,
                "last_accessed": session.last_accessed,
                "ip_address": session.ip_address
            }
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sessions"
        )
