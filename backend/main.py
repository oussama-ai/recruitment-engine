from fastapi import FastAPI
from backend.api_routes import router

app = FastAPI(title="Recruitment Engine v1.0")
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)