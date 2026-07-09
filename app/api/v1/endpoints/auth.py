from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import create_access_token
from app.crud.crud_user import user as user_crud
from app.schemas.token import Token, LoginRequest
from app.schemas.response import ApiResponse

router = APIRouter()

@router.post("/login", response_model=ApiResponse[Token])
def login_access_token(
    login_data: LoginRequest, db: Session = Depends(get_db)
) -> Any:
    """
    Login endpoint. Requires a JSON body with 'email' and 'password'.
    """
    user = user_crud.authenticate(db, email=login_data.email, password=login_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    raw_token = create_access_token(user.id)
    
    # Store token in database
    user.access_token = raw_token
    db.commit()
    
    token = Token(
        access_token=raw_token,
        token_type="bearer",
    )
    return ApiResponse(message="Login successful", data=token)


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/swagger-login", response_model=Token, include_in_schema=False)
def swagger_login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Dedicated login for Swagger UI Authorize button (which requires Form Data).
    """
    user = user_crud.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    raw_token = create_access_token(user.id)
    user.access_token = raw_token
    db.commit()
    
    return {
        "access_token": raw_token,
        "token_type": "bearer",
    }
