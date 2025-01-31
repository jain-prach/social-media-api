# from fastapi import Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address, default_limits=["5/minute"])

# LimitDep = Depends(limiter.limit(limit_value="5/minute"))