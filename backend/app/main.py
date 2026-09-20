from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    anomalies,
    chat,
    export,
    firestore,
    forecast,
    health,
    insights,
    precedents,
    statistics,
    trends,
)

app = FastAPI(
    title="Legal Trend Radar API",
    description=(
        "Statistical/time-series analysis of Korean court precedent search-result counts "
        "collected from 국가법령정보센터 (law.go.kr) Open API. NOT legal advice."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(precedents.router)
app.include_router(trends.router)
app.include_router(anomalies.router)
app.include_router(forecast.router)
app.include_router(insights.router)
app.include_router(statistics.router)
app.include_router(export.router)
app.include_router(chat.router)
app.include_router(firestore.router)
