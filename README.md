# Mitra AI Backend

A modular FastAPI backend with face recognition, voice commands, and system control capabilities.

## Features

- **Face Recognition Authentication**: Register and authenticate users using facial recognition
- **Voice Command Recognition**: Register voice profiles and execute system commands via voice
- **System Command Execution**: Secure execution of allowed system commands
- **User Management**: Complete user registration, authentication, and profile management
- **Database Integration**: PostgreSQL with async SQLAlchemy
- **Security**: JWT authentication, password hashing, command validation
- **Modular Architecture**: Clean separation of concerns with services, models, and API routes

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for session management)
- System libraries for face recognition and audio processing

### System Dependencies (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libpq-dev \
    cmake \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    libboost-python-dev \
    libboost-system-dev \
    libportaudio2 \
    libportaudio-dev \
    python3-pyaudio \
    libasound2-dev \
    libpulse-dev \
    ffmpeg
```

### macOS Dependencies

```bash
brew install cmake boost-python3 portaudio ffmpeg
```

## Installation

1. **Clone the repository** (if not already done):
   ```bash
   cd "Mitra AI/backend"
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL database**:
   ```bash
   # Create database
   sudo -u postgres psql
   CREATE DATABASE mitra_ai;
   CREATE USER mitra_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE mitra_ai TO mitra_user;
   \q
   ```

5. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

6. **Set up database tables**:
   ```bash
   python setup_database.py
   ```

## Configuration

Edit the `.env` file with your settings:

```env
# Database Configuration
DATABASE_URL=postgresql://mitra_user:your_password@localhost:5432/mitra_ai
ASYNC_DATABASE_URL=postgresql+asyncpg://mitra_user:your_password@localhost:5432/mitra_ai

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Face Recognition
FACE_RECOGNITION_TOLERANCE=0.6
MAX_FACE_ENCODINGS_PER_USER=5

# Voice Recognition  
VOICE_CONFIDENCE_THRESHOLD=0.7
VOICE_RECOGNITION_TIMEOUT=5

# System Commands (add/remove as needed)
ALLOWED_SYSTEM_COMMANDS=["ls", "pwd", "whoami", "date", "uptime", "df", "free", "top"]

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Running the Server

1. **Development mode**:
   ```bash
   python main.py
   ```

2. **Production mode with Uvicorn**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

3. **With SSL (production)**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
   ```

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with username/password
- `POST /api/v1/auth/logout` - Logout current user
- `GET /api/v1/auth/me` - Get current user info

### Face Recognition
- `POST /api/v1/face/register` - Register face encoding
- `POST /api/v1/face/authenticate` - Authenticate via face recognition
- `GET /api/v1/face/encodings` - Get user's face encodings
- `DELETE /api/v1/face/encodings/{id}` - Delete face encoding
- `POST /api/v1/face/verify` - Verify face against current user

### Voice Recognition
- `POST /api/v1/voice/register` - Register voice profile
- `POST /api/v1/voice/authenticate` - Authenticate via voice
- `GET /api/v1/voice/profiles` - Get user's voice profiles
- `DELETE /api/v1/voice/profiles/{id}` - Delete voice profile

### System Commands
- `POST /api/v1/commands/execute` - Execute system command
- `POST /api/v1/commands/voice-execute` - Execute voice command
- `GET /api/v1/commands/history` - Get command history
- `GET /api/v1/commands/allowed` - Get allowed commands
- `GET /api/v1/commands/system-info` - Get system information

### Users
- `GET /api/v1/users/profile` - Get user profile
- `PUT /api/v1/users/profile` - Update user profile
- `GET /api/v1/users/stats` - Get user statistics
- `GET /api/v1/users/activity` - Get user activity
- `DELETE /api/v1/users/account` - Delete user account

## Usage Examples

### Face Registration
```bash
curl -X POST "http://localhost:8000/api/v1/face/register" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_data": "base64_encoded_image_data",
    "encoding_name": "primary"
  }'
```

### Voice Command Execution
```bash
curl -X POST "http://localhost:8000/api/v1/commands/voice-execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "audio_data": "base64_encoded_audio_data"
  }'
```

### System Command Execution
```bash
curl -X POST "http://localhost:8000/api/v1/commands/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls",
    "args": ["-la"],
    "timeout": 30
  }'
```

## Development

### Project Structure
```
backend/
├── app/
│   ├── api/
│   │   └── routes/          # API route handlers
│   ├── core/               # Core configuration and database
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   └── services/           # Business logic services
├── uploads/                # File uploads (created at runtime)
├── logs/                   # Application logs (created at runtime)
├── main.py                 # FastAPI application
├── setup_database.py       # Database setup script
└── requirements.txt        # Python dependencies
```

### Adding New Commands
1. Add command to `ALLOWED_SYSTEM_COMMANDS` in `.env`
2. Update `parse_voice_command()` in `SystemCommandService` for voice recognition
3. Test command execution through API

### Security Considerations
- Commands are validated against an allowed list
- Dangerous patterns are blocked
- Commands run in a restricted environment
- User input is sanitized
- JWT tokens expire after configured time
- Passwords are hashed with bcrypt

## Troubleshooting

### Common Issues

1. **Face recognition library installation fails**:
   ```bash
   pip install --no-cache-dir dlib
   pip install face-recognition
   ```

2. **Audio processing issues**:
   ```bash
   # Install system audio libraries first
   sudo apt-get install portaudio19-dev python3-pyaudio
   pip install pyaudio
   ```

3. **PostgreSQL connection issues**:
   - Verify database credentials in `.env`
   - Check PostgreSQL service is running
   - Verify database exists and user has permissions

4. **Permission denied for system commands**:
   - Check command is in allowed list
   - Verify user permissions
   - Check system security policies

### Logs
Application logs are stored in `./logs/app.log`. Check for detailed error messages.

## Contributing

1. Follow the existing code structure
2. Add tests for new features
3. Update documentation
4. Ensure security best practices
5. Test with both development and production configurations

## License

This project is part of the Mitra AI system. See the main project LICENSE file for details.
