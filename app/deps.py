from fastapi import Request
from services import JagritiService


async def get_jagriti_service(request: Request) -> JagritiService:
    return request.app.state.jagriti_service
