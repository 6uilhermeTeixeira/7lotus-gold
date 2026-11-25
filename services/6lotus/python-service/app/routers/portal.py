"""Authenticated HTML portal routes."""

from collections.abc import Callable

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from ..auth import (
    SESSION_COOKIE_NAME,
    create_session_value,
    has_valid_session,
    password_matches,
    read_login_password,
)
from ..config import Settings
from ..pages import (
    render_account_page,
    render_catalog_page,
    render_comparison_page,
    render_growth_simulator_page,
    render_history_page,
    render_login_page,
    render_operations_page,
)
from ..schemas import BotCatalogItem
from ..security import RateLimit, client_key, rate_limiter
from ..workspace import render_workspace


def create_portal_router(
    settings: Settings,
    *,
    list_bots: Callable[[bool | None], list[BotCatalogItem]],
    require_page_session: Callable[[Request], RedirectResponse | None],
    local_preview: Callable[[Request], bool],
    operational_bot_ids: frozenset[str] | set[str],
) -> APIRouter:
    router = APIRouter(include_in_schema=False)

    @router.get("/")
    def root(request: Request) -> RedirectResponse:
        target = "/workspace" if local_preview(request) or has_valid_session(request, settings) else "/login"
        return RedirectResponse(url=target, status_code=303)

    @router.get("/workspace", response_class=HTMLResponse, response_model=None)
    def workspace_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return render_workspace("Pesquisa", 7775, (
            ("strategies", "Estratégias", "/bots?workspace=1"),
            ("account", "Conta", "/account?workspace=1"),
            ("comparison", "Comparar estratégias", "/compare?workspace=1"),
            ("simulator", "Simulador de crescimento", "/growth-simulator?workspace=1"),
            ("health", "Saúde operacional", "/operations?workspace=1"),
            ("history", "Histórico do ouro", "/history?workspace=1&source=fusion"),
        ))

    @router.get("/login", response_class=HTMLResponse, response_model=None)
    def login_page(request: Request, error: str | None = None) -> HTMLResponse | RedirectResponse:
        if local_preview(request):
            return RedirectResponse(url="/workspace", status_code=303)
        if has_valid_session(request, settings):
            return RedirectResponse(url="/workspace", status_code=303)
        if error == "config" or not settings.dashboard_auth_configured:
            return render_login_page("O acesso ainda nao foi configurado neste ambiente.", status_code=503)
        return render_login_page()

    @router.post("/login", response_model=None)
    async def login(request: Request) -> RedirectResponse | HTMLResponse:
        if not settings.dashboard_auth_configured:
            return render_login_page("O acesso ainda nao foi configurado neste ambiente.", status_code=503)
        rate_key = client_key(request, "login")
        rate_limiter.check(rate_key, RateLimit(settings.login_rate_limit_attempts, 300))
        if not password_matches(await read_login_password(request), settings):
            return render_login_page("Senha invalida.", status_code=401)
        rate_limiter.reset(rate_key)
        response = RedirectResponse(url="/workspace", status_code=303)
        response.set_cookie(
            SESSION_COOKIE_NAME,
            create_session_value(settings),
            max_age=settings.session_max_age_seconds,
            httponly=True,
            secure=request.url.scheme == "https" or request.url.hostname not in {"127.0.0.1", "localhost", "::1"},
            samesite="lax",
            path="/",
        )
        return response

    @router.post("/logout")
    def logout() -> RedirectResponse:
        response = RedirectResponse(url="/login", status_code=303)
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")
        return response

    @router.get("/bots", response_class=HTMLResponse, response_model=None)
    def bots_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return render_catalog_page(list_bots(True))

    @router.get("/compare", response_class=HTMLResponse, response_model=None)
    def comparison_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return render_comparison_page(list_bots(True))

    @router.get("/growth-simulator", response_class=HTMLResponse, response_model=None)
    def growth_simulator_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return render_growth_simulator_page(list_bots(True))

    @router.get("/history", response_class=HTMLResponse, response_model=None)
    def history_page(request: Request, source: str = "dukascopy") -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        if source not in {"dukascopy", "fusion"}:
            raise HTTPException(status_code=404, detail="history source not found")
        return render_history_page(source)

    @router.get("/operations", response_class=HTMLResponse, response_model=None)
    def operations_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return render_operations_page()

    @router.get("/account", response_class=HTMLResponse, response_model=None)
    def account_page(request: Request) -> HTMLResponse | RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        bots = [bot for bot in list_bots(True) if bot.id in operational_bot_ids]
        return render_account_page(bots)

    @router.get("/results")
    def legacy_results(request: Request) -> RedirectResponse:
        if redirect := require_page_session(request):
            return redirect
        return RedirectResponse(url="/bots", status_code=303)

    return router
