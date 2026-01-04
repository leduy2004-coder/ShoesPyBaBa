from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React default
            "http://localhost:5173",  # Vite default
            "http://localhost:8080",  # Vite default
            # Add your frontend URL here
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
