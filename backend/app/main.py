from fastapi import FastAPI

from .api.auth import router as auth_router
from .api.users import router as users_router


def create_app() -> FastAPI:
    app = FastAPI(title="LIMS API")
    app.include_router(auth_router)
    app.include_router(users_router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
