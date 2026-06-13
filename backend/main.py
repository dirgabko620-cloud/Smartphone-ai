import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, EmailStr
import jwt
from passlib.context import CryptContext
from sqlalchemy import create_engine, Column, String, DateTime, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smartphone_ai.db")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Initialize FastAPI app
app = FastAPI(
    title="Smartphone AI API",
    description="Advanced AI Website API for Termux",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# ==================== Models ====================

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    message = Column(Text)
    response = Column(Text)
    model_used = Column(String, default="ollama")
    created_at = Column(DateTime, default=datetime.utcnow)

class GeneratedContent(Base):
    __tablename__ = "generated_content"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    content_type = Column(String)  # image, code, text
    prompt = Column(Text)
    result = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models
class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ChatRequest(BaseModel):
    message: str
    model: str = "ollama"

class ChatResponse(BaseModel):
    id: int
    message: str
    response: str
    model_used: str
    created_at: datetime

    class Config:
        from_attributes = True

class ImageGenerationRequest(BaseModel):
    prompt: str
    size: str = "512x512"
    model: str = "stable-diffusion"

class CodeGenerationRequest(BaseModel):
    prompt: str
    language: str = "python"
    model: str = "ollama"

# ==================== Utilities ====================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthCredentials) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        return {"username": username, "user_id": payload.get("user_id")}
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# ==================== Routes ====================

# Health Check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "Smartphone AI API"}

# Authentication Routes
@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate token
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/auth/profile", response_model=UserResponse)
async def get_profile(credentials: HTTPAuthCredentials = Depends(security), db: Session = Depends(get_db)):
    """Get user profile"""
    token_data = verify_token(credentials)
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user

# Chat Routes
@app.post("/api/chat", response_model=ChatResponse)
async def chat(
    chat_req: ChatRequest,
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Send message to AI"""
    token_data = verify_token(credentials)
    
    # Here you would integrate with actual AI models
    # For now, returning a simple response
    response_text = f"AI Response to: {chat_req.message}"
    
    chat_message = ChatMessage(
        user_id=token_data["user_id"],
        message=chat_req.message,
        response=response_text,
        model_used=chat_req.model
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    return chat_message

@app.get("/api/chat/history")
async def get_chat_history(
    limit: int = 50,
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get chat history"""
    token_data = verify_token(credentials)
    
    messages = db.query(ChatMessage).filter(
        ChatMessage.user_id == token_data["user_id"]
    ).order_by(ChatMessage.created_at.desc()).limit(limit).all()
    
    return messages

# Image Generation Route
@app.post("/api/generate/image")
async def generate_image(
    req: ImageGenerationRequest,
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Generate image from prompt"""
    token_data = verify_token(credentials)
    
    # Here you would integrate with image generation models
    result = {
        "status": "processing",
        "prompt": req.prompt,
        "size": req.size,
        "model": req.model
    }
    
    content = GeneratedContent(
        user_id=token_data["user_id"],
        content_type="image",
        prompt=req.prompt,
        result=str(result)
    )
    db.add(content)
    db.commit()
    
    return result

# Code Generation Route
@app.post("/api/generate/code")
async def generate_code(
    req: CodeGenerationRequest,
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Generate code from prompt"""
    token_data = verify_token(credentials)
    
    # Here you would integrate with code generation models
    result = {
        "status": "generating",
        "prompt": req.prompt,
        "language": req.language,
        "model": req.model
    }
    
    content = GeneratedContent(
        user_id=token_data["user_id"],
        content_type="code",
        prompt=req.prompt,
        result=str(result)
    )
    db.add(content)
    db.commit()
    
    return result

# Data Analysis Route
@app.post("/api/analyze")
async def analyze_data(
    data: dict,
    credentials: HTTPAuthCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Analyze data"""
    token_data = verify_token(credentials)
    
    return {
        "status": "analyzing",
        "analysis": "Analysis results will appear here"
    }

# ==================== Initialization ====================

# Create tables
Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )