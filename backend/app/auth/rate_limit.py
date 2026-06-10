from time import time

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings
from app.shared.exceptions.application import ForbiddenError

_local_attempts: dict[str, list[float]] = {}


def check_login_rate_limit(email: str, ip_address: str | None) -> None:
    key = f"login:{email.lower()}:{ip_address or 'unknown'}"
    settings = get_settings()
    try:
        redis = Redis.from_url(settings.redis_url, socket_connect_timeout=0.2, socket_timeout=0.2)
        count = redis.incr(key)
        if count == 1:
            redis.expire(key, 300)
        if count > 10:
            raise ForbiddenError("Too many login attempts")
    except RedisError:
        now = time()
        attempts = [item for item in _local_attempts.get(key, []) if now - item < 300]
        attempts.append(now)
        _local_attempts[key] = attempts
        if len(attempts) > 10:
            raise ForbiddenError("Too many login attempts") from None
