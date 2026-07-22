from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api import deps
from app.services.auth_service import auth_service
from app.core import security
from app.schemas.external import ExternalUserResponse, TokenValidationResponse, PermissionResponse
from app.schemas.user import User, UserCreate
from app.services.user_service import user_service
import uuid

router = APIRouter()

# All endpoints here require API Key
@router.post("/login", 
    dependencies=[Depends(deps.verify_api_key)],
    summary="External Application Login",
    description="Allows a registered application to authenticate users via email and password.")
def external_login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Standard OAuth2 password flow for external applications.
    Returns an access token scoped for the authenticated user.
    """
    user = auth_service.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    session = auth_service.create_session(db, user_id=user.id)
    access_token = security.create_access_token(
        data={"sub": str(user.id), "jti": session.token_jti, "roles": [role.name for role in user.roles]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/validate-token", 
    response_model=TokenValidationResponse, 
    dependencies=[Depends(deps.verify_api_key)],
    summary="Validate JWT Token",
    description="Verifies the validity and active session status of a provided JWT Bearer token.")
def validate_token(payload: dict = Depends(deps.get_token_payload), db: Session = Depends(get_db)):
    """
    Checks if a token's JTI exists in active sessions and has not been revoked.
    """
    token_jti = payload.get("jti")
    is_active = auth_service.is_session_active(db, token_jti)
    
    return {
        "is_valid": is_active,
        "user_id": payload.get("sub"),
        "session_id": token_jti,
        "expires_at": payload.get("exp")
    }

@router.get("/get-user", 
    response_model=ExternalUserResponse,
    summary="Get User Information",
    description="Retrieves profile and role information for a user by ID or Email.")
def get_user_info(
    user_id: Optional[uuid.UUID] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    app = Depends(deps.verify_api_credentials)
):
    """
    Required: API Credentials (API Key + API Secret).
    """
    if not user_id and not email:
        raise HTTPException(status_code=400, detail="Either user_id or email must be provided")
    
    if user_id:
        user = user_service.get_user_by_id(db, user_id)
    else:
        user = user_service.get_user_by_email(db, email)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return {
        "user_id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "roles": [role.name for role in user.roles]
    }

@router.get("/get-permissions", 
    response_model=PermissionResponse,
    summary="Get User Permissions",
    description="Retrieves a flat list of unique permissions assigned to a user via their roles.")
def get_user_permissions(
    user_id: Optional[uuid.UUID] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    app = Depends(deps.verify_api_credentials)
):
    """
    Required: API Credentials (API Key + API Secret).
    Used for RBAC checks in downstream services.
    """
    if not user_id and not email:
        raise HTTPException(status_code=400, detail="Either user_id or email must be provided")
        
    if user_id:
        user = user_service.get_user_by_id(db, user_id)
    else:
        user = user_service.get_user_by_email(db, email)
        
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    permissions = []
    for role in user.roles:
        permissions.extend(role.permissions)
    
    # Remove duplicates
    seen = set()
    unique_perms = []
    for p in permissions:
        if p.id not in seen:
            unique_perms.append(p)
            seen.add(p.id)
            
    return {
        "user_id": user.id,
        "permissions": unique_perms
    }

@router.post("/create-user", 
    response_model=ExternalUserResponse,
    summary="Create External User",
    description="Allows registered applications to register new users on the platform.")
def create_external_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    app = Depends(deps.verify_api_credentials)
):
    """
    Create a new user on the portal. This endpoint is restricted to 
    registered applications with valid API credentials.
    """
    try:
        user = user_service.create_user(db, user_in=user_in)
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"User creation failed: {str(e)}")

@router.put("/update-user",
    response_model=ExternalUserResponse,
    summary="Update External User",
    description="Allows registered applications to update user information.")
def update_external_user(
    user_id: uuid.UUID,
    user_in: dict, # Using dict to allow partial updates without strict UserUpdate schema if needed
    db: Session = Depends(get_db),
    app = Depends(deps.verify_api_credentials)
):
    """
    Update an existing user on the portal.
    """
    try:
        from app.schemas.user import UserUpdate
        update_data = UserUpdate(**user_in)
        user = user_service.update_user(db, user_id=user_id, user_in=update_data)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "roles": [role.name for role in user.roles]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
