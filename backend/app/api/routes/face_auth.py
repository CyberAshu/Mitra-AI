from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import base64
import logging

from app.core.database import get_async_db
from app.services.face_recognition_service import FaceRecognitionService
from app.schemas.user import FaceAuthRequest, FaceAuthResponse, Token, UserResponse
from app.api.routes.auth import get_current_user, auth_service
from app.models.user import User, AuthSession
from datetime import datetime, timedelta

router = APIRouter()
logger = logging.getLogger(__name__)
face_service = FaceRecognitionService()


@router.post("/register", response_model=dict)
async def register_face(
    face_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Register a face encoding for the current user"""
    try:
        if "image_data" not in face_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_data is required"
            )
        
        image_data = face_data["image_data"]
        encoding_name = face_data.get("encoding_name", "primary")
        
        result = await face_service.register_face(
            db=db,
            user_id=str(current_user.id),
            image_data=image_data,
            encoding_name=encoding_name
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
        logger.error(f"Error registering face: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face registration failed"
        )


@router.post("/authenticate", response_model=FaceAuthResponse)
async def authenticate_face(
    auth_request: FaceAuthRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Authenticate user by face recognition"""
    try:
        result = await face_service.authenticate_face(
            db=db,
            image_data=auth_request.image_data,
            tolerance=auth_request.tolerance
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
                auth_method="face",
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
            
            return FaceAuthResponse(
                success=True,
                user_id=user_id,
                confidence=result["confidence"],
                message=result["message"],
                token=token
            )
        else:
            return FaceAuthResponse(
                success=False,
                message=result["message"],
                confidence=result.get("confidence", 0.0)
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during face authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face authentication failed"
        )


@router.get("/encodings")
async def get_face_encodings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all face encodings for the current user"""
    try:
        encodings = await face_service.get_user_face_encodings(
            db=db,
            user_id=str(current_user.id)
        )
        
        return {
            "encodings": encodings,
            "count": len(encodings)
        }
        
    except Exception as e:
        logger.error(f"Error getting face encodings: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get face encodings"
        )


@router.delete("/encodings/{encoding_id}")
async def delete_face_encoding(
    encoding_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a face encoding"""
    try:
        result = await face_service.delete_face_encoding(
            db=db,
            user_id=str(current_user.id),
            encoding_id=encoding_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting face encoding: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete face encoding"
        )


@router.post("/upload")
async def upload_face_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Upload face image for registration"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Read and encode image
        image_bytes = await file.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Register face
        result = await face_service.register_face(
            db=db,
            user_id=str(current_user.id),
            image_data=image_base64,
            encoding_name=f"upload_{file.filename}"
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
        logger.error(f"Error uploading face image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image upload failed"
        )


@router.post("/verify")
async def verify_face(
    verification_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Verify if a face matches the current user's registered faces"""
    try:
        if "image_data" not in verification_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="image_data is required"
            )
        
        # Authenticate face but only for current user
        result = await face_service.authenticate_face(
            db=db,
            image_data=verification_data["image_data"],
            tolerance=verification_data.get("tolerance")
        )
        
        # Check if the recognized user is the current user
        if result["success"]:
            recognized_user_id = result["user_id"]
            is_current_user = str(current_user.id) == recognized_user_id
            
            return {
                "success": is_current_user,
                "confidence": result["confidence"],
                "message": "Face verified successfully" if is_current_user else "Face does not match current user",
                "is_current_user": is_current_user
            }
        else:
            return {
                "success": False,
                "confidence": 0.0,
                "message": "Face not recognized",
                "is_current_user": False
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error verifying face: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Face verification failed"
        )
