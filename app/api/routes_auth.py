import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.user import User
from app.schemas.auth_schema import (
    AuthRequest, 
    AuthResponse, 
    RegisterRequest, 
    PasswordResetRequest, 
    SessionDetailResponse,
    RevokeSessionRequest,
    Verify2FARequest,
    TwoFactorToggleRequest,
    TwoFactorResponse,
    TwoFactorVerifyResponse
)
from app.services.supabase_service import SupabaseService
from app.core.jwt_auth import JWTBearer
from typing import List
import logging
from supabase import create_client

logger = logging.getLogger(__name__)
router = APIRouter()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

supabase_service = SupabaseService()

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user with rollback support for both Supabase and database operations.
    """
    supabase_uid = None
    try:
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        user_metadata = {
            "first_name": request.first_name,
            "last_name": request.last_name,
            "role": request.role,
            "title": request.title,
            "phone": request.phone,
            "id_type": request.id_type,
            "nic_passport": request.nic_passport,
        }
        supabase_response = await supabase_service.sign_up(
            email=request.email,
            password=request.password,
            user_metadata=user_metadata
        )
        supabase_uid = supabase_response["supabase_uid"]
        db_user = User(
            supabase_uid=supabase_uid,
            email=request.email,
            title=request.title,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            id_type=request.id_type,
            nic_passport=request.nic_passport,
            role=request.role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return AuthResponse(
            message="Registration successful. Please log in.",
            user_id=db_user.user_id,
            access_token=None,
            user=None
        )
    except Exception as e:
        db.rollback()
        if supabase_uid:
            try:
                await supabase_service.delete_user(supabase_uid)
            except Exception as supabase_error:
                logger.error(f"Failed to delete Supabase user during rollback: {str(supabase_error)}")
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=AuthResponse)
async def login(
    request: AuthRequest,
    db: Session = Depends(get_db)
):
    """
    Step 1: Verify email and password, then send 2FA code if enabled.
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })
        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        if user.two_factor_enabled:
            otp_response = supabase.auth.sign_in_with_otp({
                "email": request.email,
                "options": {
                    "should_create_user": False
                }
            })
            if not otp_response:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to send 2FA code"
                )
            return AuthResponse(
                message="2FA code sent to your email",
                requires_2fa=True,
                user_id=user.user_id
            )
        else:
            return AuthResponse(
                message="Login successful",
                requires_2fa=False,
                access_token=auth_response.session.access_token,
                user_id=user.user_id,
                user={
                    "email": user.email,
                    "first_name": user.first_name,
                    "role": user.role,
                    "profile_picture_url": user.profile_picture_url
                }
            )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{str(e)}"
        )

@router.post("/verify-2fa", response_model=TwoFactorVerifyResponse)
async def verify_2fa(
    request: Verify2FARequest,
    db: Session = Depends(get_db)
):
    """
    Step 2: Verify the 2FA code and create a session.
    """
    try:
        verification_result = supabase.auth.verify_otp({
            "email": request.email,
            "token": request.token,
            "type": "email"
        })
        if not verification_result.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found in database"
            )
        return TwoFactorVerifyResponse(
            message="2FA verification successful",
            access_token=verification_result.session.access_token,
            user_id=user.user_id,
            user={
                "email": user.email,
                "first_name": user.first_name,
                "role": user.role,
                "profile_picture_url": user.profile_picture_url
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error verifying 2FA code: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to verify 2FA code"
        )

@router.post("/toggle-2fa", response_model=TwoFactorResponse)
async def toggle_2fa(
    request: TwoFactorToggleRequest,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Enable or disable 2FA for the authenticated user.
    """
    try:
        current_user.two_factor_enabled = request.enabled
        db.commit()
        db.refresh(current_user)
        metadata = {"two_factor_enabled": request.enabled}
        await supabase_service.update_user_metadata(current_user.supabase_uid, metadata)
        return TwoFactorResponse(
            message="2FA settings updated successfully",
            two_factor_enabled=current_user.two_factor_enabled
        )
    except Exception as e:
        logger.error(f"Error updating 2FA settings: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update 2FA settings"
        )

@router.post("/logout")
async def logout():
    """
    Log out the authenticated user.
    """
    try:
        await supabase_service.sign_out()
        return {"message": "Logout successful"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest):
    """
    Send a password reset email to the user.
    """
    try:
        if not request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        await supabase_service.reset_password(request.email)
        return {"message": "Password reset email sent"}
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to send password reset email"
        )

@router.get("/active-sessions", response_model=List[SessionDetailResponse])
async def get_active_sessions(
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Retrieve active sessions for the authenticated user.
    """
    try:
        sessions = supabase_service.get_active_sessions(current_user.supabase_uid)
        if not sessions:
            return []
        user_sessions = []
        for session in sessions:
            session_response = SessionDetailResponse(
                user_id=current_user.user_id,
                supabase_uid=current_user.supabase_uid,
                role=current_user.role,
                email=session.get('email') or current_user.email,
                session_id=session.get('session_id'),
                ip_address=session.get('ip_address'),
                user_agent=session.get('user_agent'),
                last_sign_in_at=session.get('last_sign_in_at'),
                created_at=session.get('created_at'),
                updated_at=session.get('updated_at'),
                current_session_id=session.get('current_session_id')
            )
            user_sessions.append(session_response)
        return user_sessions
    except Exception as e:
        logger.error(f"Error fetching active sessions: {str(e)}")
        return []

@router.post("/revoke-sessions")
async def revoke_sessions(
    request: RevokeSessionRequest,
    current_user: User = Depends(JWTBearer()),
    db: Session = Depends(get_db)
):
    """
    Revoke user sessions based on the request.
    """
    try:
        if request.session_id:
            logger.warning("Specific session revocation not yet implemented")
        if request.revoke_all:
            result = supabase_service.revoke_user_sessions(current_user.supabase_uid)
        return {"message": "Sessions revoked successfully"}
    except Exception as e:
        logger.error(f"Session revocation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke sessions"
        )
