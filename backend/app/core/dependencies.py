"""FastAPI dependencies for security and validation."""
from fastapi import HTTPException, status, Header
from typing import Optional

from app.core.security import is_license_valid


async def require_valid_license(
    x_license_key: Optional[str] = Header(None)
) -> bool:
    """
    Dependency to require valid license key.
    
    Checks license in order:
    1. X-License-Key header
    2. LICENSE_KEY environment variable
    3. Open-source mode (no license required)
    
    Raises:
        HTTPException: 403 if license is invalid
    
    Returns:
        True if license is valid
    
    Usage:
        @app.get("/api/premium-feature", dependencies=[Depends(require_valid_license)])
        async def premium_feature():
            return {"status": "success"}
    """
    if not is_license_valid(x_license_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing license key. Please contact your administrator."
        )
    
    return True


async def check_license() -> dict:
    """
    Check license status (for admin/health endpoints).
    
    Returns:
        Dict with license status information
    """
    is_valid = is_license_valid()
    
    return {
        "license_required": bool(os.getenv("LICENSE_KEY")),
        "license_valid": is_valid,
        "mode": "open-source" if not os.getenv("LICENSE_KEY") else "licensed"
    }


import os
