from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_async_db
from app.schemas.user import UserResponse, UserUpdate
from app.api.routes.auth import get_current_user
from app.models.user import User, CommandHistory, FaceEncoding, VoiceProfile

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user's profile"""
    return UserResponse.from_orm(current_user)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update current user's profile"""
    try:
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if field == "password":
                # Hash password
                from app.api.routes.auth import auth_service
                current_user.hashed_password = auth_service.hash_password(value)
            elif hasattr(current_user, field):
                setattr(current_user, field, value)
        
        await db.commit()
        await db.refresh(current_user)
        
        logger.info(f"User profile updated: {current_user.username}")
        return UserResponse.from_orm(current_user)
        
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )


@router.get("/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user statistics"""
    try:
        # Get command statistics
        command_stats_stmt = select(
            CommandHistory.command_type,
            func.count(CommandHistory.id).label('count'),
            func.avg(CommandHistory.execution_time).label('avg_execution_time')
        ).where(
            CommandHistory.user_id == current_user.id
        ).group_by(CommandHistory.command_type)
        
        command_stats_result = await db.execute(command_stats_stmt)
        command_stats = command_stats_result.fetchall()
        
        # Get total commands
        total_commands_stmt = select(func.count(CommandHistory.id)).where(
            CommandHistory.user_id == current_user.id
        )
        total_commands_result = await db.execute(total_commands_stmt)
        total_commands = total_commands_result.scalar()
        
        # Get face encodings count
        face_encodings_stmt = select(func.count(FaceEncoding.id)).where(
            FaceEncoding.user_id == current_user.id
        )
        face_encodings_result = await db.execute(face_encodings_stmt)
        face_encodings_count = face_encodings_result.scalar()
        
        # Get voice profiles count
        voice_profiles_stmt = select(func.count(VoiceProfile.id)).where(
            VoiceProfile.user_id == current_user.id
        )
        voice_profiles_result = await db.execute(voice_profiles_stmt)
        voice_profiles_count = voice_profiles_result.scalar()
        
        # Get recent successful commands
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_success_stmt = select(func.count(CommandHistory.id)).where(
            CommandHistory.user_id == current_user.id,
            CommandHistory.execution_status == 'success',
            CommandHistory.executed_at >= seven_days_ago
        )
        recent_success_result = await db.execute(recent_success_stmt)
        recent_successful_commands = recent_success_result.scalar()
        
        return {
            "user_id": str(current_user.id),
            "username": current_user.username,
            "account_created": current_user.created_at,
            "last_login": current_user.last_login,
            "total_commands": total_commands or 0,
            "recent_successful_commands": recent_successful_commands or 0,
            "face_encodings": face_encodings_count or 0,
            "voice_profiles": voice_profiles_count or 0,
            "command_stats": [
                {
                    "command_type": stat.command_type,
                    "count": stat.count,
                    "avg_execution_time": float(stat.avg_execution_time) if stat.avg_execution_time else 0.0
                }
                for stat in command_stats
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.get("/activity")
async def get_user_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get recent user activity"""
    try:
        # Get recent commands
        commands_stmt = select(CommandHistory).where(
            CommandHistory.user_id == current_user.id
        ).order_by(CommandHistory.executed_at.desc()).limit(min(limit, 50))
        
        commands_result = await db.execute(commands_stmt)
        recent_commands = commands_result.scalars().all()
        
        activity = []
        
        for cmd in recent_commands:
            activity.append({
                "type": "command",
                "timestamp": cmd.executed_at,
                "details": {
                    "command": cmd.command,
                    "command_type": cmd.command_type,
                    "status": cmd.execution_status,
                    "execution_time": cmd.execution_time
                }
            })
        
        # Sort by timestamp (most recent first)
        activity.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "activity": activity[:limit],
            "count": len(activity)
        }
        
    except Exception as e:
        logger.error(f"Error getting user activity: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user activity"
        )


@router.delete("/account")
async def delete_user_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete user account and all associated data"""
    try:
        # Note: Due to cascade relationships, this will also delete:
        # - Face encodings
        # - Voice profiles  
        # - Command history
        # - Auth sessions
        
        await db.delete(current_user)
        await db.commit()
        
        logger.info(f"User account deleted: {current_user.username}")
        
        return {
            "success": True,
            "message": "Account deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Error deleting user account: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Account deletion failed"
        )


@router.post("/export-data")
async def export_user_data(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Export all user data"""
    try:
        # Get all user data
        user_data = {
            "user_profile": {
                "id": str(current_user.id),
                "username": current_user.username,
                "email": current_user.email,
                "full_name": current_user.full_name,
                "created_at": current_user.created_at.isoformat(),
                "last_login": current_user.last_login.isoformat() if current_user.last_login else None
            }
        }
        
        # Get face encodings info (without the actual encoding data for privacy)
        face_encodings_stmt = select(FaceEncoding).where(FaceEncoding.user_id == current_user.id)
        face_encodings_result = await db.execute(face_encodings_stmt)
        face_encodings = face_encodings_result.scalars().all()
        
        user_data["face_encodings"] = [
            {
                "id": str(encoding.id),
                "encoding_name": encoding.encoding_name,
                "is_primary": encoding.is_primary,
                "created_at": encoding.created_at.isoformat()
            }
            for encoding in face_encodings
        ]
        
        # Get voice profiles info (without the actual voice features)
        voice_profiles_stmt = select(VoiceProfile).where(VoiceProfile.user_id == current_user.id)
        voice_profiles_result = await db.execute(voice_profiles_stmt)
        voice_profiles = voice_profiles_result.scalars().all()
        
        user_data["voice_profiles"] = [
            {
                "id": str(profile.id),
                "profile_name": profile.profile_name,
                "wake_phrase": profile.wake_phrase,
                "is_active": profile.is_active,
                "created_at": profile.created_at.isoformat()
            }
            for profile in voice_profiles
        ]
        
        # Get command history
        command_history_stmt = select(CommandHistory).where(
            CommandHistory.user_id == current_user.id
        ).order_by(CommandHistory.executed_at.desc()).limit(1000)  # Limit to last 1000 commands
        
        command_history_result = await db.execute(command_history_stmt)
        command_history = command_history_result.scalars().all()
        
        user_data["command_history"] = [
            {
                "id": str(cmd.id),
                "command": cmd.command,
                "command_type": cmd.command_type,
                "execution_status": cmd.execution_status,
                "execution_time": cmd.execution_time,
                "executed_at": cmd.executed_at.isoformat()
            }
            for cmd in command_history
        ]
        
        return {
            "success": True,
            "data": user_data,
            "exported_at": datetime.utcnow().isoformat(),
            "data_types": [
                "user_profile",
                "face_encodings_metadata",
                "voice_profiles_metadata", 
                "command_history"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error exporting user data: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Data export failed"
        )
