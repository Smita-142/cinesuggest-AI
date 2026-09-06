from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import engine

from routes.movies import router as movies_router
from routes.auth import router as auth_router
from routes.ratings import router as ratings_router
from routes.favorites import router as favorites_router
from routes.watch_history import router as watch_history_router
from routes.recommendations import router as recommendations_router


app = FastAPI(
    title="CineMatch-AI API",
    description="Movie Recommendation Engine Backend",
    version="1.0.0"
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "CineMatch-AI API is running!"
    }


@app.get("/health")
def health():
    try:
        with engine.connect():
            return {
                "status": "OK",
                "database": "MySQL connected successfully"
            }
    except Exception as e:
        return {
            "status": "ERROR",
            "database": "MySQL connection failed",
            "error": str(e)
        }


app.include_router(movies_router)
app.include_router(auth_router)
app.include_router(ratings_router)
app.include_router(favorites_router)
app.include_router(watch_history_router)
app.include_router(recommendations_router)
