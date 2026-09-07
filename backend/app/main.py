from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from .api.auth import router as auth_router
from .api.users import router as users_router
from .config import get_settings


def _static_dist(static_dir: str | None) -> Path | None:
    """有效 dist 目录（存在且含 index.html）→ 绝对路径；否则 None。"""
    if not static_dir:
        return None
    d = Path(static_dir)
    if d.is_dir() and (d / "index.html").is_file():
        return d.resolve()
    return None


def _mount_spa(app: FastAPI, dist: Path) -> None:
    """SPA 托管（注册在所有 /api 路由之后）：

    - /api/ 前缀未命中 → JSON 404（不吞 API 错误）
    - dist 内真实文件 → FileResponse 直出（自动 content-type）
    - 其余路径 → index.html（SPA 路由回退）
    - is_relative_to 守卫防路径穿越
    """

    @app.api_route(
        "/api/{path:path}",
        methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        include_in_schema=False,
    )
    async def api_404(path: str):
        # catch-all 仅 GET，未注册 API 的非 GET 方法会被 starlette 答 405；
        # 统一为 404（注册在 catch-all 之前，已注册的 /api 路由优先）
        raise HTTPException(status_code=404)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_or_static(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404)
        file = (dist / full_path).resolve()
        if full_path and file.is_file() and file.is_relative_to(dist):
            return FileResponse(file)
        return FileResponse(dist / "index.html")


def create_app(static_dir: str | None = None) -> FastAPI:
    app = FastAPI(title="LIMS API")
    app.include_router(auth_router)
    app.include_router(users_router)

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    dist = _static_dist(static_dir)
    if dist is not None:
        _mount_spa(app, dist)

    return app


app = create_app(get_settings().static_dir)
