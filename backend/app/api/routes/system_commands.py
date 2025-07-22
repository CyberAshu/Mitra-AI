from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.database import get_async_db
from app.services.system_command_service import SystemCommandService
from app.services.voice_recognition_service import VoiceRecognitionService
from app.schemas.user import SystemCommandRequest, SystemCommandResponse
from app.api.routes.auth import get_current_user
from app.models.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
command_service = SystemCommandService()
voice_service = VoiceRecognitionService()


@router.post("/execute", response_model=SystemCommandResponse)
async def execute_command(
    command_request: SystemCommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Execute a system command"""
    try:
        result = await command_service.execute_command(
            db=db,
            user_id=str(current_user.id),
            command=command_request.command,
            args=command_request.args,
            timeout=command_request.timeout,
            command_type="manual"
        )
        
        return SystemCommandResponse(**result)
        
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Command execution failed"
        )


@router.post("/voice-execute")
async def execute_voice_command(
    voice_command_data: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Execute a command from voice input"""
    try:
        if "audio_data" not in voice_command_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="audio_data is required"
            )
        
        # First, transcribe the voice command
        transcription_result = await voice_service.transcribe_audio(
            voice_command_data["audio_data"]
        )
        
        if not transcription_result["success"]:
            return {
                "success": False,
                "message": "Could not transcribe voice command",
                "error": transcription_result["message"]
            }
        
        transcribed_text = transcription_result["transcribed_text"]
        
        # Parse the voice command to system command
        parse_result = await command_service.parse_voice_command(transcribed_text)
        
        if not parse_result["success"]:
            return {
                "success": False,
                "message": parse_result["message"],
                "transcribed_text": transcribed_text,
                "suggestions": parse_result.get("suggestions", [])
            }
        
        # Execute the parsed command
        execution_result = await command_service.execute_command(
            db=db,
            user_id=str(current_user.id),
            command=parse_result["command"],
            args=parse_result["args"],
            timeout=30,
            command_type="voice"
        )
        
        return {
            "success": execution_result["success"],
            "transcribed_text": transcribed_text,
            "parsed_command": f"{parse_result['command']} {' '.join(parse_result['args'])}",
            "description": parse_result["description"],
            "output": execution_result.get("output"),
            "error": execution_result.get("error"),
            "execution_time": execution_result["execution_time"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing voice command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice command execution failed"
        )


@router.get("/history")
async def get_command_history(
    limit: int = 50,
    command_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get command execution history for the current user"""
    try:
        history = await command_service.get_command_history(
            db=db,
            user_id=str(current_user.id),
            limit=min(limit, 100),  # Cap at 100
            command_type=command_type
        )
        
        return {
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting command history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get command history"
        )


@router.get("/allowed")
async def get_allowed_commands():
    """Get list of allowed system commands"""
    return {
        "allowed_commands": command_service.allowed_commands,
        "max_command_length": command_service.max_command_length,
        "examples": [
            {"command": "ls", "description": "List directory contents", "example": "ls -la"},
            {"command": "pwd", "description": "Print working directory", "example": "pwd"},
            {"command": "whoami", "description": "Show current user", "example": "whoami"},
            {"command": "date", "description": "Show current date and time", "example": "date"},
            {"command": "uptime", "description": "Show system uptime", "example": "uptime"},
            {"command": "df", "description": "Show disk usage", "example": "df -h"},
            {"command": "free", "description": "Show memory usage", "example": "free -h"},
            {"command": "top", "description": "Show running processes", "example": "top -bn1"},
            {"command": "ps", "description": "Show process status", "example": "ps aux"},
            {"command": "netstat", "description": "Show network connections", "example": "netstat -an"}
        ]
    }


@router.get("/system-info")
async def get_system_info():
    """Get current system information"""
    try:
        system_info = await command_service.get_system_info()
        
        return {
            "success": True,
            "system_info": system_info
        }
        
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get system information"
        )


@router.post("/parse-voice")
async def parse_voice_command(
    voice_text: dict,
    current_user: User = Depends(get_current_user)
):
    """Parse natural language to system command"""
    try:
        if "text" not in voice_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="text is required"
            )
        
        result = await command_service.parse_voice_command(voice_text["text"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing voice command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Voice command parsing failed"
        )


@router.post("/validate")
async def validate_command(
    command_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Validate if a command is allowed to be executed"""
    try:
        if "command" not in command_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="command is required"
            )
        
        command = command_data["command"]
        args = command_data.get("args", [])
        
        validation_result = command_service._validate_command(command, args)
        
        return {
            "valid": validation_result["valid"],
            "reason": validation_result.get("reason"),
            "command": command,
            "full_command": f"{command} {' '.join(args)}" if args else command
        }
        
    except Exception as e:
        logger.error(f"Error validating command: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Command validation failed"
        )
