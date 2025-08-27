from redis.asyncio import Redis

class AsyncRedisCircuitBreaker:
    def __init__(self, redis_url, fail_max, reset_timeout, state_name):
        self.redis_url = redis_url
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.state_name = state_name
        self._redis = None

    def get_instance(self):
        if not self._redis:
            self._redis = Redis.from_url(self.redis_url, decode_responses=True)
        return self._redis

    async def get_failure_count(self):
        redis = self.get_instance()
        count = await redis.get(f"cb:{self.state_name}:fail_count")
        return int(count or 0)

    async def increment_failure_count(self):
        redis = self.get_instance()
        return await redis.incr(f"cb:{self.state_name}:fail_count")

    async def reset(self):
        redis = self.get_instance()
        await redis.delete(f"cb:{self.state_name}:fail_count", f"cb:{self.state_name}:state")

    async def set_state(self, state):
        redis = self.get_instance()
        await redis.set(f"cb:{self.state_name}:state", state)

    async def get_state(self):
        redis = self.get_instance()
        state = await redis.get(f"cb:{self.state_name}:state")
        return state or "closed"

    async def fail(self):
        count = await self.increment_failure_count()
        if count >= self.fail_max:
            await self.set_state("open")
        else:
            await self.set_state("closed")

    async def success(self):
        await self.reset()
        await self.set_state("closed")

    async def can_execute(self):
        state = await self.get_state()
        return state == "closed"
