from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
import base64
import logging

from app.core.database import get_async_db
from app.services.voice_recognition_service import VoiceRecognitionService
from app.schemas.user import VoiceAuthRequest, VoiceAuthResponse, Token, UserResponse
from app.api.routes.auth import get_current_user, auth_service
from app.models.user import User, AuthSession, VoiceProfile
from sqlalchemy import select
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)
voice_service = VoiceRecognitionService()


@router.post("/register", response_model=dict)
async def register_voice(
    voice_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Register a voice profile for the current user"""
    try:
        if "audio_data" not in voice_data or "wake_phrase" not in voice_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio_data and wake_phrase are required"
            )
        
        audio_data = voice_data["audio_data"]
        wake_phrase = voice_data["wake_phrase"]
        profile_name = voice_data.get("profile_name", "primary")
        
        result = await voice_service.register_voice(
            db=db,
            user_id=str(current_user.id),
            audio_data=audio_data,
            wake_phrase=wake_phrase,
            profile_name=profile_name
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering voice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice registration failed"
        )


@router.post("/authenticate", response_model=VoiceAuthResponse)
async def authenticate_voice(
    auth_request: VoiceAuthRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user by voice recognition"""
    try:
        result = await voice_service.authenticate_voice(
            db=db,
            audio_data=auth_request.audio_data,
            expected_phrase=auth_request.expected_phrase
        )
        
        if result["success"]:
            # Create access token
            user_id = result["user_id"]
            username = result["username"]
            
            access_token_expires = timedelta(minutes=30)
            access_token = auth_service.create_access_token(
                data={"sub": username, "user_id": user_id},
                expires_delta=access_token_expires
            )
            
            # Create auth session
            auth_session = AuthSession(
                user_id=user_id,
                session_token=access_token,
                auth_method="voice",
                expires_at=datetime.utcnow() + access_token_expires,
                is_active=True
            )
            
            db.add(auth_session)
            await db.commit()
            
            # Get user for response
            from sqlalchemy import select
            stmt = select(User).where(User.id == user_id)
            db_result = await db.execute(stmt)
            user = db_result.scalar_one()
            
            token = Token(
                access_token=access_token,
                token_type="bearer",
                expires_in=30 * 60,
                user=UserResponse.from_orm(user)
            )
            
            return VoiceAuthResponse(
                success=True,
                user_id=user_id,
                recognized_text=result["transcribed_text"],
                confidence=result["confidence"],
                message=result["message"],
                token=token
            )
        else:
            return VoiceAuthResponse(
                success=False,
                message=result["message"],
                confidence=result.get("confidence", 0.0)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during voice authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice authentication failed"
        )


@router.get("/profiles")
async def get_voice_profiles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all voice profiles for the current user"""
    try:
        stmt = select(VoiceProfile).where(VoiceProfile.user_id == current_user.id)
        result = await db.execute(stmt)
        profiles = result.scalars().all()
        
        return {
            "profiles": [
                {
                    "id": str(profile.id),
                    "profile_name": profile.profile_name,
                    "wake_phrase": profile.wake_phrase,
                    "confidence_threshold": profile.confidence_threshold,
                    "is_active": profile.is_active,
                }
                for profile in profiles
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting voice profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get voice profiles"
        )


@router.delete("/profiles/{profile_id}")
async def delete_voice_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a voice profile"""
    try:
        # Query for the profile
        stmt = select(VoiceProfile).where(
            VoiceProfile.id == profile_id,
            VoiceProfile.user_id == current_user.id
        )
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voice profile not found"
            )
        
        # Delete profile
        await db.delete(profile)
        await db.commit()
        
        logger.info(f"Voice profile {profile_id} deleted for user {current_user.username}")
        
        return {"success": True, "message": "Voice profile deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting voice profile: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete voice profile"
        )
