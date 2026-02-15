from fastapi import APIRouter, Depends
from app.repositories.rate_limit.rate_limit_repository import RateLimitRepository
from app.schemas.rate_limit import RateLimitCreate, RateLimitRead, RateLimitUpdate
from app.api.dependencies import get_rate_limit_repo

rate_limit = APIRouter(
    prefix="/rate-limit",
    tags=["Rate Limit"],
)


@rate_limit.post("/", response_model=RateLimitRead)
async def create_rule(
    data: RateLimitCreate,
    repo: RateLimitRepository = Depends(get_rate_limit_repo),
):
    return await repo.create(data)


@rate_limit.get("/", response_model=list[RateLimitRead])
async def list_rules(
    repo: RateLimitRepository = Depends(get_rate_limit_repo),
):
    return await repo.get_active_rules()

@rate_limit.get("/{rule_id}", response_model=RateLimitRead)
async def get_rule(
    rule_id: int,
    repo: RateLimitRepository = Depends(get_rate_limit_repo),
):
    return await repo.get(rule_id)

@rate_limit.put("/{rule_id}", response_model=RateLimitRead)
async def update_rule(
    rule_id: int,
    data: RateLimitUpdate,
    repo: RateLimitRepository = Depends(get_rate_limit_repo),
):
    rule = await repo.get(rule_id)
    if not rule:
        return {"error": "Rule not found"}
    return await repo.update(rule, data)