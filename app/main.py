from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from . import router
from .exceptions import UniqueViolationException


app = FastAPI(
    title="StatisticsCounterService",
    version="0.1",
    description="A service for maintaining statistics. It is possible"
    "to update statistics (add new ones and add new ones to the old one), "
    "view statistics for a certain period of time with filtering, "
    "and also clean up all available statistics.",
)

# Include statistics routers (/api/statistics)
app.include_router(
    router.router,
    prefix="/api",
    tags=["statistics"]
)


@app.exception_handler(UniqueViolationException)
def unique_violation_exception_handler(
        request: Request, exception: UniqueViolationException
):
    return JSONResponse(
        status_code=400,
        content={"message": "An object with such a key already exists"}
    )
