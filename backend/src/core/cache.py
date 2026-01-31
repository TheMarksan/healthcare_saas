from datetime import datetime, timedelta
from typing import TypeVar, Generic, Callable, Awaitable
from dataclasses import dataclass

T = TypeVar('T')


@dataclass
class CacheEntry(Generic[T]):
    value: T
    expires_at: datetime


class SimpleCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
    
    def get(self, key: str) -> T | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        if datetime.utcnow() > entry.expires_at:
            del self._cache[key]
            return None
        return entry.value
    
    def set(self, key: str, value: T, ttl: int | None = None) -> None:
        ttl = ttl or self._default_ttl
        self._cache[key] = CacheEntry(
            value=value,
            expires_at=datetime.utcnow() + timedelta(seconds=ttl)
        )
    
    def delete(self, key: str) -> None:
        self._cache.pop(key, None)
    
    def clear(self) -> None:
        self._cache.clear()
    
    async def get_or_set(
        self, 
        key: str, 
        factory: Callable[[], Awaitable[T]], 
        ttl: int | None = None
    ) -> T:
        cached = self.get(key)
        if cached is not None:
            return cached
        value = await factory()
        self.set(key, value, ttl)
        return value


cache = SimpleCache(default_ttl=300)
