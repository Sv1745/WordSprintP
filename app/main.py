from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.config import SECRET_KEY
from app.database import fetch_one
from app.routers import auth, game, admin

app = FastAPI(
    title="WordSprint API",
    description="Python FastAPI backend for WordSprint application",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="SESSIONID",
    same_site="lax"
)

# API Routers
app.include_router(auth.router)
app.include_router(game.router)
app.include_router(admin.router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

@app.get("/db-health")
def db_health_check():
    try:
        user_count = fetch_one("SELECT COUNT(*) as count FROM users")
        return {
            "status": "connected",
            "user_count": user_count["count"] if user_count else 0
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }

# Mount Static Files (Serving HTML, CSS, JS frontend)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
