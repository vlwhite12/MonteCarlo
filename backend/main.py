"""
FastAPI application entry point for the Texas Hold'em Equity Calculator.
"""

import multiprocessing
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import router

app = FastAPI(
    title="Texas Hold'em Equity Calculator",
    description="Monte Carlo simulation engine for poker hand equity",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
