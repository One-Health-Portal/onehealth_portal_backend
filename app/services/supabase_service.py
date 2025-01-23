import os
import logging
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()
logger = logging.getLogger(__name__)

class SupabaseService:
    def __init__(self):
        # Initialize Supabase client
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )

    async def sign_up(self, email: str, password: str, user_metadata: Dict) -> Dict:
        """
        Register a new user with Supabase.
        """
        try:
            response = self.supabase.auth.admin.create_user({
                "email": email,
                "password": password,
                "email_confirm": True,
                "user_metadata": user_metadata
            })
            if not response.user:
                raise Exception("User creation failed")
            return {
                "supabase_uid": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata,
            }
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise Exception(f"Failed to create user: {str(e)}")

    def sign_in_with_password(self, email: str, password: str):
        """
        Authenticate a user with email and password.
        """
        try:
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            if not response.session:
                raise Exception("Authentication failed")
            return response.session
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            raise Exception("Invalid credentials")

    async def send_2fa_code(self, email: str):
        """
        Send a 2FA code (OTP) to the user's email.
        """
        try:
            # Use the `sign_in_with_otp` method with type="email" to send an OTP
            response = self.supabase.auth.sign_in_with_otp({
                "email": email,
                "options": {
                    "should_create_user": False,  # Do not create a new user
                    "email_redirect_to": None,   # Disable magic link redirection
                }
            })
            logger.info(f"2FA code sent to: {email}")
            return response
        except Exception as e:
            logger.error(f"Error sending 2FA code: {str(e)}")
            raise Exception("Failed to send 2FA code")

    async def verify_2fa(self, email: str, token: str):
        """
        Verify the 2FA code entered by the user.
        """
        try:
            response = self.supabase.auth.verify_otp({
                "email": email,
                "token": token,
                "type": "email"
            })
            return response
        except Exception as e:
            logger.error(f"Error verifying 2FA code: {str(e)}")
            raise Exception("Failed to verify 2FA code")

    async def sign_out(self):
        """
        Sign out the current user.
        """
        try:
            self.supabase.auth.sign_out()
            logger.info("User signed out successfully")
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            raise Exception("Failed to sign out")

    async def reset_password(self, email: str):
        """
        Send a password reset email to the user.
        """
        try:
            self.supabase.auth.reset_password_for_email(email)
            logger.info(f"Password reset email sent to: {email}")
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            raise Exception("Failed to send password reset email")

    async def update_user_metadata(self, supabase_uid: str, metadata: Dict) -> Dict:
        """
        Update user metadata in Supabase using the admin API.
        
        Args:
            supabase_uid (str): The user's Supabase UID
            metadata (Dict): The metadata to update
            
        Returns:
            Dict: The updated user data
        """
        try:
            # Use the admin API to update user metadata
            response = self.supabase.auth.admin.update_user_by_id(
                supabase_uid,
                {
                    "user_metadata": metadata
                }
            )
            
            if not response.user:
                raise Exception("Failed to update user metadata")
                
            logger.info(f"Successfully updated metadata for user: {supabase_uid}")
            return {
                "supabase_uid": response.user.id,
                "email": response.user.email,
                "user_metadata": response.user.user_metadata,
            }
        except Exception as e:
            logger.error(f"Error updating user metadata: {str(e)}")
            raise Exception(f"Failed to update user metadata: {str(e)}")
    
    def get_active_sessions(self, supabase_uid: str) -> List[Dict[str, Optional[str]]]:
        """
        Retrieve active sessions for a specific Supabase user.
        """
        try:
            user_response = self.supabase.auth.admin.get_user_by_id(supabase_uid)
            if not user_response or not user_response.user:
                logger.warning(f"No user found for UID: {supabase_uid}")
                return []
            
            session_details = [
                {
                    "session_id": user_response.user.id,
                    "email": user_response.user.email,
                    "last_sign_in_at": user_response.user.last_sign_in_at,
                    "created_at": user_response.user.created_at,
                    "updated_at": user_response.user.updated_at,
                    "role": user_response.user.user_metadata.get('role') if user_response.user.user_metadata else None,
                    "current_session_id": None
                }
            ]
            return session_details
        except Exception as e:
            logger.error(f"Error retrieving active sessions: {str(e)}")
            return []

    def revoke_user_sessions(self, supabase_uid: str) -> bool:
        """
        Revoke all active sessions for a specific Supabase user.
        """
        try:
            self.supabase.auth.admin.revoke_refresh_tokens(supabase_uid)
            logger.info(f"Successfully revoked all sessions for user: {supabase_uid}")
            return True
        except Exception as e:
            logger.error(f"Error revoking user sessions: {str(e)}")
            raise Exception(f"Failed to revoke user sessions: {str(e)}")