import face_recognition
import numpy as np
import cv2
import base64
import io
import pickle
from PIL import Image
from typing import List, Optional, Tuple, Dict
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, FaceEncoding
from app.core.config import get_settings
import logging
import os
import uuid

settings = get_settings()
logger = logging.getLogger(__name__)


class FaceRecognitionService:
    def __init__(self):
        self.tolerance = settings.face_recognition_tolerance
        self.max_encodings_per_user = settings.max_face_encodings_per_user
        
    async def register_face(
        self, 
        db: AsyncSession, 
        user_id: str, 
        image_data: str, 
        encoding_name: str = "primary"
    ) -> Dict:
        """Register a new face encoding for a user"""
        try:
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            if image is None:
                return {"success": False, "message": "Invalid image data"}
            
            # Detect faces and generate encodings
            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                return {"success": False, "message": "No face detected in image"}
            
            if len(face_locations) > 1:
                return {"success": False, "message": "Multiple faces detected. Please use an image with only one face"}
            
            # Generate face encoding
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                return {"success": False, "message": "Could not generate face encoding"}
            
            face_encoding = face_encodings[0]
            
            # Check if user already has too many encodings
            stmt = select(FaceEncoding).where(FaceEncoding.user_id == user_id)
            result = await db.execute(stmt)
            existing_encodings = result.scalars().all()
            
            if len(existing_encodings) >= self.max_encodings_per_user:
                return {
                    "success": False, 
                    "message": f"Maximum number of face encodings ({self.max_encodings_per_user}) reached"
                }
            
            # Save image file
            image_filename = f"{user_id}_{encoding_name}_{uuid.uuid4()}.jpg"
            image_path = os.path.join(settings.faces_dir, image_filename)
            
            # Convert numpy array back to PIL Image and save
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            pil_image.save(image_path, "JPEG", quality=95)
            
            # Serialize encoding
            encoding_bytes = pickle.dumps(face_encoding)
            
            # Create database record
            db_encoding = FaceEncoding(
                user_id=user_id,
                encoding_name=encoding_name,
                encoding_data=encoding_bytes,
                image_path=image_path,
                confidence_score=1.0,
                is_primary=(len(existing_encodings) == 0)  # First encoding is primary
            )
            
            db.add(db_encoding)
            await db.commit()
            await db.refresh(db_encoding)
            
            logger.info(f"Face encoding registered for user {user_id}")
            return {
                "success": True,
                "message": "Face encoding registered successfully",
                "encoding_id": str(db_encoding.id),
                "is_primary": db_encoding.is_primary
            }
            
        except Exception as e:
            logger.error(f"Error registering face: {str(e)}")
            await db.rollback()
            return {"success": False, "message": f"Error registering face: {str(e)}"}
    
    async def authenticate_face(
        self, 
        db: AsyncSession, 
        image_data: str, 
        tolerance: Optional[float] = None
    ) -> Dict:
        """Authenticate a user by their face"""
        try:
            # Use custom tolerance or default
            auth_tolerance = tolerance or self.tolerance
            
            # Decode base64 image
            image = self._decode_base64_image(image_data)
            if image is None:
                return {"success": False, "message": "Invalid image data"}
            
            # Detect faces in the image
            face_locations = face_recognition.face_locations(image)
            if not face_locations:
                return {"success": False, "message": "No face detected in image"}
            
            if len(face_locations) > 1:
                return {"success": False, "message": "Multiple faces detected. Please ensure only one face is visible"}
            
            # Generate face encoding for the input image
            face_encodings = face_recognition.face_encodings(image, face_locations)
            if not face_encodings:
                return {"success": False, "message": "Could not generate face encoding"}
            
            input_encoding = face_encodings[0]
            
            # Get all face encodings from database
            stmt = select(FaceEncoding, User).join(User).where(User.is_active == True)
            result = await db.execute(stmt)
            encodings_with_users = result.all()
            
            if not encodings_with_users:
                return {"success": False, "message": "No registered faces found"}
            
            # Compare with all registered encodings
            best_match = None
            best_distance = float('inf')
            
            for face_encoding_record, user in encodings_with_users:
                try:
                    # Deserialize stored encoding
                    stored_encoding = pickle.loads(face_encoding_record.encoding_data)
                    
                    # Calculate distance
                    distance = face_recognition.face_distance([stored_encoding], input_encoding)[0]
                    
                    if distance < auth_tolerance and distance < best_distance:
                        best_distance = distance
                        best_match = {
                            'user': user,
                            'encoding': face_encoding_record,
                            'distance': distance,
                            'confidence': 1 - distance  # Convert distance to confidence
                        }
                        
                except Exception as e:
                    logger.error(f"Error comparing encoding for user {user.id}: {str(e)}")
                    continue
            
            if best_match:
                # Update last login time
                best_match['user'].last_login = func.now()
                await db.commit()
                
                logger.info(f"Face authentication successful for user {best_match['user'].username}")
                return {
                    "success": True,
                    "message": "Face authentication successful",
                    "user_id": str(best_match['user'].id),
                    "username": best_match['user'].username,
                    "confidence": round(best_match['confidence'], 3),
                    "encoding_name": best_match['encoding'].encoding_name
                }
            else:
                logger.warning("Face authentication failed - no matching face found")
                return {
                    "success": False, 
                    "message": "Face not recognized",
                    "confidence": 0.0
                }
                
        except Exception as e:
            logger.error(f"Error during face authentication: {str(e)}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    async def get_user_face_encodings(
        self, 
        db: AsyncSession, 
        user_id: str
    ) -> List[Dict]:
        """Get all face encodings for a user"""
        try:
            stmt = select(FaceEncoding).where(FaceEncoding.user_id == user_id)
            result = await db.execute(stmt)
            encodings = result.scalars().all()
            
            return [
                {
                    "id": str(encoding.id),
                    "encoding_name": encoding.encoding_name,
                    "confidence_score": encoding.confidence_score,
                    "is_primary": encoding.is_primary,
                    "created_at": encoding.created_at,
                    "image_path": encoding.image_path
                }
                for encoding in encodings
            ]
            
        except Exception as e:
            logger.error(f"Error getting face encodings for user {user_id}: {str(e)}")
            return []
    
    async def delete_face_encoding(
        self, 
        db: AsyncSession, 
        user_id: str, 
        encoding_id: str
    ) -> Dict:
        """Delete a face encoding"""
        try:
            # Get the encoding
            stmt = select(FaceEncoding).where(
                FaceEncoding.id == encoding_id,
                FaceEncoding.user_id == user_id
            )
            result = await db.execute(stmt)
            encoding = result.scalar_one_or_none()
            
            if not encoding:
                return {"success": False, "message": "Face encoding not found"}
            
            # Delete image file if it exists
            if encoding.image_path and os.path.exists(encoding.image_path):
                try:
                    os.remove(encoding.image_path)
                except Exception as e:
                    logger.warning(f"Could not delete image file {encoding.image_path}: {str(e)}")
            
            # Delete from database
            await db.delete(encoding)
            await db.commit()
            
            logger.info(f"Face encoding {encoding_id} deleted for user {user_id}")
            return {"success": True, "message": "Face encoding deleted successfully"}
            
        except Exception as e:
            logger.error(f"Error deleting face encoding {encoding_id}: {str(e)}")
            await db.rollback()
            return {"success": False, "message": f"Error deleting face encoding: {str(e)}"}
    
    def _decode_base64_image(self, image_data: str) -> Optional[np.ndarray]:
        """Decode base64 image data to numpy array"""
        try:
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Convert to PIL Image
            pil_image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            # Convert to numpy array for face_recognition
            image_array = np.array(pil_image)
            
            return image_array
            
        except Exception as e:
            logger.error(f"Error decoding base64 image: {str(e)}")
            return None
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better face recognition"""
        try:
            # Convert BGR to RGB if necessary
            if len(image.shape) == 3 and image.shape[2] == 3:
                # Assume it's in RGB format already
                pass
            
            # Resize if image is too large (for performance)
            height, width = image.shape[:2]
            if width > 1200 or height > 1200:
                scale_factor = min(1200/width, 1200/height)
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                image = cv2.resize(image, (new_width, new_height))
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            return image
