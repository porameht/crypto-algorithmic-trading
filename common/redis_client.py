import redis
from datetime import timedelta

class RedisClient:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
    def set_alert(self, symbol: str, alert_type: str, expiry_hours: int = 1):
        """Set alert state with expiry time"""
        key = f"alert:{symbol}:{alert_type}"
        self.redis.setex(key, timedelta(hours=expiry_hours), "1")
        
    def was_alerted(self, symbol: str, alert_type: str) -> bool:
        """Check if symbol was already alerted"""
        key = f"alert:{symbol}:{alert_type}"
        return bool(self.redis.exists(key)) 