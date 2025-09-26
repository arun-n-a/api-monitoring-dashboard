from fastapi import Depends, HTTPException, status, Path
from app.core.security import get_current_user_from_header_token

def admin_required(current_user=Depends(get_current_user_from_header_token)):
    if current_user['role_id'] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user



def is_self_user_or_admin(
    user_id: str = Path(...),
    current_user=Depends(get_current_user_from_header_token)
):
    if current_user['id'] != user_id and current_user['role_id'] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data"
        )
    return current_user