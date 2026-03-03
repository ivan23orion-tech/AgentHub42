from collections import deque
from time import time

from fastapi import Header, HTTPException

WINDOW_SECONDS = 60
MAX_REQUESTS_PER_AGENT = 30
_agent_hits: dict[str, deque[float]] = {}


def get_agent_id(x_agent_id: str | None = Header(default=None)) -> str:
    if not x_agent_id or not x_agent_id.strip():
        raise HTTPException(status_code=400, detail="Missing required header: X-Agent-Id")

    agent_id = x_agent_id.strip()
    now = time()
    queue = _agent_hits.setdefault(agent_id, deque())

    while queue and now - queue[0] > WINDOW_SECONDS:
        queue.popleft()

    if len(queue) >= MAX_REQUESTS_PER_AGENT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded for this agent")

    queue.append(now)
    return agent_id
