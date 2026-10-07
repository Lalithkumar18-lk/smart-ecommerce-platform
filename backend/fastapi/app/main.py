from fastapi import FastAPI

app = FastAPI(
    title="Smart E-Commerce Platform API",
    description="FastAPI backend for the customer/user panel",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "Smart E-Commerce Platform API is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }