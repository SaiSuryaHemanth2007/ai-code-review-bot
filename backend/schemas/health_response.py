from pydantic import BaseModel


class ServiceStatus(BaseModel):
    groq: bool
    gemini: bool
    cache: bool
    database: bool
    github: bool


class HealthResponse(BaseModel):
    status: str
    version: str
    services: ServiceStatus