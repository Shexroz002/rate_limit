from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.dependencies import get_rate_limit_repo
from app.workers.scheduler import start_scheduler, scheduler
from app.workers.tasks import RateLimitRuleUpdater

repo =  get_rate_limit_repo()
updater = RateLimitRuleUpdater(repo)

@asynccontextmanager
async def lifespan(app: FastAPI):

    start_scheduler(updater)
    print("App started, Redis initialized, scheduler running")

    yield  # bu yerda app ishlaydi


    scheduler.shutdown()
    print("App shutdown, Redis closed, scheduler stopped")


app = FastAPI(lifespan=lifespan)



