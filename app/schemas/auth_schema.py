from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime

# Authentication and Registration Models
class AuthRequest(BaseModel):
    """Request model for login"""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

class RegisterRequest(BaseModel):
    """Request model for user registration"""
    title: str = Field(..., description="User's title (e.g., Mr., Mrs., Master)")
    first_name: str = Field(..., description="User's first name")
    last_name: str = Field(..., description="User's last name")
    phone: str = Field(..., description="User's phone number")
    id_type: str = Field(..., description="User's ID type (e.g., NIC, Passport)")
    nic_passport: str = Field(..., description="User's NIC or Passport number")
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    role: str = Field(default="Patient", description="User's role (e.g., Patient, Admin, Staff)")

class AuthResponse(BaseModel):
    """Response model for authentication"""
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")  # Make it optional with a default
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="Access token for authenticated sessions")
    user_id: Optional[int] = Field(None, description="Local database user ID")
    user: Optional[Dict[str, Any]] = Field(None, description="User details")

class PasswordResetRequest(BaseModel):
    """Request model for password reset"""
    email: EmailStr = Field(..., description="User's email address")

# Session Management Models
class SessionDetailResponse(BaseModel):
    """Detailed representation of a user's active session"""
    session_id: Optional[str] = Field(None, description="Unique identifier for the session")
    user_id: Optional[int] = Field(None, description="Local database user ID")
    supabase_uid: Optional[str] = Field(None, description="Supabase user unique identifier")
    email: Optional[str] = Field(None, description="User's email address")
    role: Optional[str] = Field(None, description="User's role")
    
    # Session-specific details
    ip_address: Optional[str] = Field(None, description="IP address of the session")
    user_agent: Optional[str] = Field(None, description="User agent string")
    
    # Timestamp fields
    last_sign_in_at: Optional[datetime] = Field(None, description="Timestamp of last sign-in")
    created_at: Optional[datetime] = Field(None, description="Session creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    # Additional session metadata
    current_session_id: Optional[str] = Field(None, description="Current active session identifier")
    sign_in_count: Optional[int] = Field(default=0, description="Number of sign-ins")

class RevokeSessionRequest(BaseModel):
    """Request model for revoking user sessions"""
    session_id: Optional[str] = Field(None, description="Specific session to revoke")
    revoke_all: bool = Field(default=False, description="Flag to revoke all user sessions")

# Two-Factor Authentication (2FA) Models
class Verify2FARequest(BaseModel):
    """Request model for verifying 2FA code"""
    email: EmailStr = Field(..., description="User's email address")
    token: str = Field(..., description="The 2FA verification code")

class TwoFactorToggleRequest(BaseModel):
    enabled: bool  # Change from `enable` to `enabled`
    method: str = "email"  # Optional field for 2FA method

class TwoFactorVerifyResponse(BaseModel):
    """Response model for 2FA verification"""
    message: str = Field(..., description="Response message")
    access_token: Optional[str] = Field(None, description="Access token for authenticated sessions")
    user_id: Optional[int] = Field(None, description="Local database user ID")
    user: Optional[Dict[str, Any]] = Field(None, description="User details")

class TwoFactorResponse(BaseModel):
    """Response model for 2FA operations"""
    message: str = Field(..., description="Response message")
    method: Optional[str] = Field(None, description="2FA method used: 'email' or 'sms'")
    access_token: Optional[str] = Field(None, description="Access token for authenticated sessions")
    user_id: Optional[int] = Field(None, description="Local database user ID")
    user: Optional[Dict[str, Any]] = Field(None, description="User details")

class TwoFactorStatusResponse(BaseModel):
    """Response model for 2FA status"""
    enabled: bool = Field(..., description="Whether 2FA is enabled for the user")
    method: Optional[str] = Field(None, description="2FA method: 'email' or 'sms'")
    user_id: int = Field(..., description="Local database user ID")
    email: str = Field(..., description="User's email address")
    phone: Optional[str] = Field(None, description="User's phone number")