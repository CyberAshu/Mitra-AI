import speech_recognition as sr
import numpy as np
import base64
import io
import json
import os
import uuid
import asyncio
from typing import Dict, List, Optional, Tuple
from pydub import AudioSegment
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User, VoiceProfile
from app.core.config import get_settings
import logging
import whisper
import librosa
from scipy.spatial.distance import cosine
import pickle
import tempfile

settings = get_settings()
logger = logging.getLogger(__name__)


class VoiceRecognitionService:
    def __init__(self):
        self.confidence_threshold = settings.voice_confidence_threshold
        self.recognition_timeout = settings.voice_recognition_timeout
        self.phrase_time_limit = settings.voice_phrase_time_limit
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        # Load Whisper model for better accuracy (optional)
        try:
            self.whisper_model = whisper.load_model("base")
            self.use_whisper = True
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.warning(f"Could not load Whisper model: {str(e)}, falling back to Google Speech Recognition")
            self.use_whisper = False
    
    async def register_voice(
        self, 
        db: AsyncSession, 
        user_id: str, 
        audio_data: str, 
        wake_phrase: str,
        profile_name: str = "primary"
    ) -> Dict:
        """Register a new voice profile for a user"""
        try:
            # Decode and process audio
            audio_array, sample_rate = self._decode_base64_audio(audio_data)
            if audio_array is None:
                return {"success": False, "message": "Invalid audio data"}
            
            # Extract voice features
            voice_features = self._extract_voice_features(audio_array, sample_rate)
            if voice_features is None:
                return {"success": False, "message": "Could not extract voice features"}
            
            # Verify the wake phrase in the audio
            transcribed_text = await self._transcribe_audio(audio_array, sample_rate)
            if not self._verify_wake_phrase(transcribed_text, wake_phrase):
                return {
                    "success": False, 
                    "message": f"Wake phrase '{wake_phrase}' not clearly detected in audio. Transcribed: '{transcribed_text}'"
                }
            
            # Save audio file
            audio_filename = f"{user_id}_{profile_name}_{uuid.uuid4()}.wav"
            audio_path = os.path.join(settings.audio_dir, audio_filename)
            self._save_audio_array(audio_array, sample_rate, audio_path)
            
            # Serialize voice features
            features_json = json.dumps({
                'mfcc_features': voice_features['mfcc'].tolist(),
                'pitch_features': voice_features['pitch'].tolist(),
                'spectral_features': voice_features['spectral'],
                'sample_rate': sample_rate
            })
            
            # Create database record
            voice_profile = VoiceProfile(
                user_id=user_id,
                profile_name=profile_name,
                audio_file_path=audio_path,
                voice_features=features_json,
                wake_phrase=wake_phrase.lower().strip(),
                confidence_threshold=self.confidence_threshold,
                is_active=True
            )
            
            db.add(voice_profile)
            await db.commit()
            await db.refresh(voice_profile)
            
            logger.info(f"Voice profile registered for user {user_id}")
            return {
                "success": True,
                "message": "Voice profile registered successfully",
                "profile_id": str(voice_profile.id),
                "wake_phrase": wake_phrase,
                "transcribed_text": transcribed_text
            }
            
        except Exception as e:
            logger.error(f"Error registering voice: {str(e)}")
            await db.rollback()
            return {"success": False, "message": f"Error registering voice: {str(e)}"}
    
    async def authenticate_voice(
        self, 
        db: AsyncSession, 
        audio_data: str,
        expected_phrase: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Dict:
        """Authenticate a user by their voice"""
        try:
            # Decode audio
            audio_array, sample_rate = self._decode_base64_audio(audio_data)
            if audio_array is None:
                return {"success": False, "message": "Invalid audio data"}
            
            # Transcribe audio
            transcribed_text = await self._transcribe_audio(audio_array, sample_rate)
            if not transcribed_text:
                return {"success": False, "message": "Could not transcribe audio"}
            
            # Extract voice features
            input_features = self._extract_voice_features(audio_array, sample_rate)
            if input_features is None:
                return {"success": False, "message": "Could not extract voice features"}
            
            # Query voice profiles
            if user_id:
                # Authenticate specific user
                stmt = select(VoiceProfile, User).join(User).where(
                    VoiceProfile.user_id == user_id,
                    VoiceProfile.is_active == True,
                    User.is_active == True
                )
            else:
                # Search all active voice profiles
                stmt = select(VoiceProfile, User).join(User).where(
                    VoiceProfile.is_active == True,
                    User.is_active == True
                )
            
            result = await db.execute(stmt)
            profiles_with_users = result.all()
            
            if not profiles_with_users:
                return {"success": False, "message": "No voice profiles found"}
            
            # Compare with stored profiles
            best_match = None
            best_similarity = 0.0
            
            for voice_profile, user in profiles_with_users:
                try:
                    # Check wake phrase if expected
                    wake_phrase_match = True
                    if expected_phrase:
                        wake_phrase_match = self._verify_wake_phrase(transcribed_text, expected_phrase)
                    elif voice_profile.wake_phrase:
                        wake_phrase_match = self._verify_wake_phrase(transcribed_text, voice_profile.wake_phrase)
                    
                    if not wake_phrase_match:
                        continue
                    
                    # Calculate voice similarity
                    similarity = self._calculate_voice_similarity(
                        input_features, 
                        voice_profile.voice_features
                    )
                    
                    if similarity > voice_profile.confidence_threshold and similarity > best_similarity:
                        best_similarity = similarity
                        best_match = {
                            'user': user,
                            'profile': voice_profile,
                            'similarity': similarity,
                            'transcribed_text': transcribed_text
                        }
                        
                except Exception as e:
                    logger.error(f"Error comparing voice profile for user {user.id}: {str(e)}")
                    continue
            
            if best_match:
                # Update last login time
                best_match['user'].last_login = func.now()
                await db.commit()
                
                logger.info(f"Voice authentication successful for user {best_match['user'].username}")
                return {
                    "success": True,
                    "message": "Voice authentication successful",
                    "user_id": str(best_match['user'].id),
                    "username": best_match['user'].username,
                    "confidence": round(best_match['similarity'], 3),
                    "transcribed_text": transcribed_text,
                    "profile_name": best_match['profile'].profile_name
                }
            else:
                logger.warning("Voice authentication failed - no matching voice found")
                return {
                    "success": False,
                    "message": "Voice not recognized",
                    "confidence": 0.0,
                    "transcribed_text": transcribed_text
                }
                
        except Exception as e:
            logger.error(f"Error during voice authentication: {str(e)}")
            return {"success": False, "message": f"Authentication error: {str(e)}"}
    
    async def transcribe_audio(
        self,
        audio_data: str
    ) -> Dict:
        """Transcribe audio to text"""
        try:
            audio_array, sample_rate = self._decode_base64_audio(audio_data)
            if audio_array is None:
                return {"success": False, "message": "Invalid audio data"}
            
            transcribed_text = await self._transcribe_audio(audio_array, sample_rate)
            
            return {
                "success": True,
                "transcribed_text": transcribed_text,
                "confidence": 0.9  # Placeholder confidence
            }
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return {"success": False, "message": f"Transcription error: {str(e)}"}
    
    def _decode_base64_audio(self, audio_data: str) -> Tuple[Optional[np.ndarray], Optional[int]]:
        """Decode base64 audio data"""
        try:
            # Remove data URL prefix if present
            if audio_data.startswith('data:audio'):
                audio_data = audio_data.split(',')[1]
            
            # Decode base64
            audio_bytes = base64.b64decode(audio_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_bytes)
                temp_path = temp_file.name
            
            try:
                # Load audio using librosa
                audio_array, sample_rate = librosa.load(temp_path, sr=None)
                return audio_array, sample_rate
            finally:
                # Clean up temporary file
                os.unlink(temp_path)
                
        except Exception as e:
            logger.error(f"Error decoding base64 audio: {str(e)}")
            return None, None
    
    def _save_audio_array(self, audio_array: np.ndarray, sample_rate: int, output_path: str):
        """Save audio array to file"""
        try:
            # Convert to AudioSegment and save
            audio_segment = AudioSegment(
                audio_array.tobytes(),
                frame_rate=sample_rate,
                sample_width=audio_array.dtype.itemsize,
                channels=1
            )
            audio_segment.export(output_path, format="wav")
            
        except Exception as e:
            logger.error(f"Error saving audio file: {str(e)}")
            raise
    
    async def _transcribe_audio(self, audio_array: np.ndarray, sample_rate: int) -> str:
        """Transcribe audio array to text"""
        try:
            if self.use_whisper:
                # Use Whisper for transcription
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    self._save_audio_array(audio_array, sample_rate, temp_path)
                    result = self.whisper_model.transcribe(temp_path)
                    return result["text"].strip()
                finally:
                    os.unlink(temp_path)
            else:
                # Use Google Speech Recognition
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    self._save_audio_array(audio_array, sample_rate, temp_path)
                    
                    with sr.AudioFile(temp_path) as source:
                        audio = self.recognizer.record(source)
                    
                    # Try Google Speech Recognition
                    text = self.recognizer.recognize_google(audio)
                    return text.strip()
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    return ""
                except sr.RequestError as e:
                    logger.error(f"Speech recognition service error: {str(e)}")
                    return ""
                finally:
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""
    
    def _extract_voice_features(self, audio_array: np.ndarray, sample_rate: int) -> Optional[Dict]:
        """Extract voice features for speaker recognition"""
        try:
            # Extract MFCC features
            mfcc = librosa.feature.mfcc(y=audio_array, sr=sample_rate, n_mfcc=13)
            mfcc_mean = np.mean(mfcc, axis=1)
            
            # Extract pitch features
            pitches, magnitudes = librosa.piptrack(y=audio_array, sr=sample_rate)
            pitch_mean = np.mean(pitches[pitches > 0]) if np.any(pitches > 0) else 0
            
            # Extract spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_array, sr=sample_rate)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_array, sr=sample_rate)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_array, sr=sample_rate)
            
            features = {
                'mfcc': mfcc_mean,
                'pitch': np.array([pitch_mean]),
                'spectral': {
                    'centroid': float(np.mean(spectral_centroids)),
                    'rolloff': float(np.mean(spectral_rolloff)),
                    'bandwidth': float(np.mean(spectral_bandwidth))
                }
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting voice features: {str(e)}")
            return None
    
    def _calculate_voice_similarity(self, features1: Dict, features2_json: str) -> float:
        """Calculate similarity between two voice feature sets"""
        try:
            features2 = json.loads(features2_json)
            
            # Compare MFCC features
            mfcc1 = np.array(features1['mfcc'])
            mfcc2 = np.array(features2['mfcc_features'])
            mfcc_similarity = 1 - cosine(mfcc1, mfcc2)
            
            # Compare pitch features
            pitch1 = features1['pitch'][0] if len(features1['pitch']) > 0 else 0
            pitch2 = features2['pitch_features'][0] if len(features2['pitch_features']) > 0 else 0
            pitch_diff = abs(pitch1 - pitch2) / max(pitch1, pitch2, 1)
            pitch_similarity = 1 - min(pitch_diff, 1)
            
            # Compare spectral features
            spectral1 = features1['spectral']
            spectral2 = features2['spectral_features']
            
            centroid_diff = abs(spectral1['centroid'] - spectral2['centroid']) / max(spectral1['centroid'], spectral2['centroid'], 1)
            spectral_similarity = 1 - min(centroid_diff, 1)
            
            # Combined similarity (weighted average)
            overall_similarity = (0.6 * mfcc_similarity + 0.2 * pitch_similarity + 0.2 * spectral_similarity)
            
            return max(0, min(1, overall_similarity))
            
        except Exception as e:
            logger.error(f"Error calculating voice similarity: {str(e)}")
            return 0.0
    
    def _verify_wake_phrase(self, transcribed_text: str, expected_phrase: str) -> bool:
        """Verify if the transcribed text contains the expected wake phrase"""
        try:
            transcribed_lower = transcribed_text.lower().strip()
            expected_lower = expected_phrase.lower().strip()
            
            # Simple word matching (can be improved with fuzzy matching)
            transcribed_words = set(transcribed_lower.split())
            expected_words = set(expected_lower.split())
            
            # Check if at least 70% of expected words are present
            if len(expected_words) == 0:
                return True
            
            matching_words = len(transcribed_words.intersection(expected_words))
            match_ratio = matching_words / len(expected_words)
            
            return match_ratio >= 0.7
            
        except Exception as e:
            logger.error(f"Error verifying wake phrase: {str(e)}")
            return False
