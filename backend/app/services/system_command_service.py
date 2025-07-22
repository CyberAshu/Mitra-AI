import subprocess
import asyncio
import time
import shlex
import os
import psutil
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import CommandHistory
from app.core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)


class SystemCommandService:
    def __init__(self):
        self.allowed_commands = settings.allowed_system_commands
        self.max_command_length = settings.max_command_length
        
    async def execute_command(
        self,
        db: AsyncSession,
        user_id: str,
        command: str,
        args: List[str] = None,
        timeout: int = 30,
        command_type: str = "manual"
    ) -> Dict:
        """Execute a system command safely"""
        start_time = time.time()
        
        try:
            # Validate command
            validation_result = self._validate_command(command, args)
            if not validation_result["valid"]:
                # Log failed command attempt
                await self._log_command(
                    db, user_id, command, command_type, 
                    "failed", None, validation_result["reason"], 0
                )
                return {
                    "success": False,
                    "command": command,
                    "error": validation_result["reason"],
                    "execution_time": time.time() - start_time
                }
            
            # Prepare full command
            if args:
                full_command = [command] + args
            else:
                # Parse command string safely
                full_command = shlex.split(command)
            
            # Log command start
            await self._log_command(
                db, user_id, " ".join(full_command), command_type, 
                "running", None, None, 0
            )
            
            # Execute command
            try:
                # Use asyncio.create_subprocess_exec for better control
                process = await asyncio.create_subprocess_exec(
                    *full_command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=os.path.expanduser("~"),  # Run in user's home directory
                    env=self._get_safe_environment()
                )
                
                # Wait for completion with timeout
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    exit_code = process.returncode
                    
                except asyncio.TimeoutError:
                    # Kill the process if it times out
                    process.kill()
                    await process.wait()
                    
                    execution_time = time.time() - start_time
                    error_msg = f"Command timed out after {timeout} seconds"
                    
                    await self._log_command(
                        db, user_id, " ".join(full_command), command_type,
                        "failed", None, error_msg, execution_time
                    )
                    
                    return {
                        "success": False,
                        "command": " ".join(full_command),
                        "error": error_msg,
                        "execution_time": execution_time,
                        "exit_code": -1
                    }
                
                # Decode output
                stdout_str = stdout.decode('utf-8', errors='replace').strip()
                stderr_str = stderr.decode('utf-8', errors='replace').strip()
                
                execution_time = time.time() - start_time
                
                # Determine success based on exit code
                success = exit_code == 0
                status = "success" if success else "failed"
                
                # Combine output and error
                output = stdout_str
                if stderr_str and not success:
                    output = f"STDOUT:\n{stdout_str}\n\nSTDERR:\n{stderr_str}" if stdout_str else stderr_str
                elif stderr_str:
                    # Some commands output useful info to stderr even on success
                    output = f"{stdout_str}\n{stderr_str}" if stdout_str else stderr_str
                
                # Log command completion
                await self._log_command(
                    db, user_id, " ".join(full_command), command_type,
                    status, output[:1000], stderr_str[:500] if not success else None, execution_time
                )
                
                return {
                    "success": success,
                    "command": " ".join(full_command),
                    "output": output,
                    "error": stderr_str if not success else None,
                    "execution_time": execution_time,
                    "exit_code": exit_code
                }
                
            except FileNotFoundError:
                execution_time = time.time() - start_time
                error_msg = f"Command '{full_command[0]}' not found"
                
                await self._log_command(
                    db, user_id, " ".join(full_command), command_type,
                    "failed", None, error_msg, execution_time
                )
                
                return {
                    "success": False,
                    "command": " ".join(full_command),
                    "error": error_msg,
                    "execution_time": execution_time,
                    "exit_code": -1
                }
                
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Execution error: {str(e)}"
            
            logger.error(f"Error executing command '{command}': {str(e)}")
            
            try:
                await self._log_command(
                    db, user_id, command, command_type,
                    "failed", None, error_msg, execution_time
                )
            except Exception as log_error:
                logger.error(f"Error logging command: {str(log_error)}")
            
            return {
                "success": False,
                "command": command,
                "error": error_msg,
                "execution_time": execution_time
            }
    
    async def get_system_info(self) -> Dict:
        """Get system information safely"""
        try:
            system_info = {
                "cpu": {
                    "usage": psutil.cpu_percent(interval=1),
                    "count": psutil.cpu_count(),
                    "freq": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
                },
                "memory": {
                    "total": psutil.virtual_memory().total,
                    "available": psutil.virtual_memory().available,
                    "used": psutil.virtual_memory().used,
                    "percentage": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": psutil.disk_usage('/').total,
                    "used": psutil.disk_usage('/').used,
                    "free": psutil.disk_usage('/').free,
                    "percentage": psutil.disk_usage('/').percent
                },
                "network": psutil.net_io_counters()._asdict(),
                "uptime": time.time() - psutil.boot_time(),
                "processes": len(psutil.pids()),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
            }
            
            return system_info
            
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {"error": str(e)}
    
    async def get_command_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 50,
        command_type: Optional[str] = None
    ) -> List[Dict]:
        """Get command history for a user"""
        try:
            from sqlalchemy import select, desc
            
            stmt = select(CommandHistory).where(CommandHistory.user_id == user_id)
            
            if command_type:
                stmt = stmt.where(CommandHistory.command_type == command_type)
                
            stmt = stmt.order_by(desc(CommandHistory.executed_at)).limit(limit)
            
            result = await db.execute(stmt)
            history = result.scalars().all()
            
            return [
                {
                    "id": str(cmd.id),
                    "command": cmd.command,
                    "command_type": cmd.command_type,
                    "execution_status": cmd.execution_status,
                    "output": cmd.output,
                    "error_message": cmd.error_message,
                    "execution_time": cmd.execution_time,
                    "executed_at": cmd.executed_at
                }
                for cmd in history
            ]
            
        except Exception as e:
            logger.error(f"Error getting command history: {str(e)}")
            return []
    
    def _validate_command(self, command: str, args: List[str] = None) -> Dict:
        """Validate if a command is allowed to be executed"""
        try:
            # Check command length
            full_command = command
            if args:
                full_command = f"{command} {' '.join(args)}"
                
            if len(full_command) > self.max_command_length:
                return {
                    "valid": False,
                    "reason": f"Command too long (max {self.max_command_length} characters)"
                }
            
            # Extract base command
            base_command = command.split()[0] if ' ' in command else command
            
            # Check if base command is in allowed list
            if base_command not in self.allowed_commands:
                return {
                    "valid": False,
                    "reason": f"Command '{base_command}' is not allowed. Allowed commands: {', '.join(self.allowed_commands)}"
                }
            
            # Check for dangerous patterns
            dangerous_patterns = [
                '&&', '||', ';', '|', '>', '>>', '<', '`', '$(',
                'rm -rf', 'dd if=', 'mkfs', 'fdisk', 'crontab',
                'sudo', 'su ', 'chmod 777', 'chown', 'usermod',
                '/etc/passwd', '/etc/shadow', 'iptables', 'ufw'
            ]
            
            for pattern in dangerous_patterns:
                if pattern in full_command.lower():
                    return {
                        "valid": False,
                        "reason": f"Command contains dangerous pattern: '{pattern}'"
                    }
            
            return {"valid": True, "reason": None}
            
        except Exception as e:
            logger.error(f"Error validating command: {str(e)}")
            return {"valid": False, "reason": f"Validation error: {str(e)}"}
    
    def _get_safe_environment(self) -> Dict[str, str]:
        """Get a safe environment for command execution"""
        # Start with a minimal environment
        safe_env = {
            'PATH': '/usr/local/bin:/usr/bin:/bin',
            'HOME': os.path.expanduser('~'),
            'USER': os.getenv('USER', 'unknown'),
            'SHELL': '/bin/bash',
            'LANG': 'en_US.UTF-8',
            'LC_ALL': 'en_US.UTF-8'
        }
        
        # Add some safe environment variables from current environment
        safe_vars = ['TERM', 'DISPLAY', 'COLUMNS', 'LINES']
        for var in safe_vars:
            if var in os.environ:
                safe_env[var] = os.environ[var]
        
        return safe_env
    
    async def _log_command(
        self,
        db: AsyncSession,
        user_id: str,
        command: str,
        command_type: str,
        status: str,
        output: Optional[str],
        error: Optional[str],
        execution_time: float
    ):
        """Log command execution to database"""
        try:
            command_log = CommandHistory(
                user_id=user_id,
                command=command,
                command_type=command_type,
                execution_status=status,
                output=output,
                error_message=error,
                execution_time=execution_time
            )
            
            db.add(command_log)
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error logging command to database: {str(e)}")
            await db.rollback()
    
    async def parse_voice_command(self, transcribed_text: str) -> Dict:
        """Parse voice command and convert to system command"""
        try:
            text_lower = transcribed_text.lower().strip()
            
            # Define command mappings
            command_mappings = {
                # System info commands
                r"(?:show|get|check|what.*)\s*(?:system|cpu|memory|disk|network)": {
                    "command": "top",
                    "args": ["-bn1"],
                    "description": "Show system information"
                },
                r"(?:list|show).*(?:files|directory|folder)": {
                    "command": "ls",
                    "args": ["-la"],
                    "description": "List files in current directory"
                },
                r"(?:current|what).*(?:directory|folder|location)": {
                    "command": "pwd",
                    "args": [],
                    "description": "Show current directory"
                },
                r"(?:show|check|get).*(?:date|time)": {
                    "command": "date",
                    "args": [],
                    "description": "Show current date and time"
                },
                r"(?:show|check|get).*(?:uptime|how long)": {
                    "command": "uptime",
                    "args": [],
                    "description": "Show system uptime"
                },
                r"(?:show|check|get).*(?:disk|storage|space)": {
                    "command": "df",
                    "args": ["-h"],
                    "description": "Show disk usage"
                },
                r"(?:show|check|get).*(?:memory|ram)": {
                    "command": "free",
                    "args": ["-h"],
                    "description": "Show memory usage"
                },
                r"(?:show|list).*(?:processes|running)": {
                    "command": "ps",
                    "args": ["aux"],
                    "description": "Show running processes"
                },
                r"(?:who|show).*(?:am i|user|logged)": {
                    "command": "whoami",
                    "args": [],
                    "description": "Show current user"
                }
            }
            
            # Try to match command patterns
            import re
            for pattern, cmd_info in command_mappings.items():
                if re.search(pattern, text_lower):
                    return {
                        "success": True,
                        "command": cmd_info["command"],
                        "args": cmd_info["args"],
                        "description": cmd_info["description"],
                        "original_text": transcribed_text
                    }
            
            # If no pattern matches, return error
            return {
                "success": False,
                "message": f"Could not parse voice command: '{transcribed_text}'",
                "suggestions": [
                    "Try saying: 'Show system information'",
                    "Try saying: 'List files'",
                    "Try saying: 'What is the current time?'",
                    "Try saying: 'Show disk usage'"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error parsing voice command: {str(e)}")
            return {
                "success": False,
                "message": f"Error parsing command: {str(e)}"
            }
