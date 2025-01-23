from fastapi.security import HTTPBearer
from fastapi import HTTPException, Request, Depends, status
from supabase import create_client
import os
from typing import Optional
from sqlalchemy.orm import Session
from app.db.connection import get_db
from app.models.user import User

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request, db: Session = Depends(get_db)):
        credentials = await super().__call__(request)
        token = credentials.credentials
        user = await self.verify_jwt(token, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or expired token."
            )
        return user

    @staticmethod
    async def verify_jwt(token: str, db: Session) -> Optional[User]:
        """Verify the Supabase JWT and retrieve the corresponding User object."""
        try:
            # Verify the JWT and get the Supabase user
            supabase_user = supabase.auth.get_user(token)
            if not supabase_user or not supabase_user.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )

            # Fetch the corresponding User object from your database
            user = db.query(User).filter(User.supabase_uid == supabase_user.user.id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found in database"
                )

            return user  # Return the SQLAlchemy User object
        except Exception as e:
            # Handle any exceptions (e.g., invalid token, network errors)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )