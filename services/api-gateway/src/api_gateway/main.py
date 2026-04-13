from fastapi import FastAPI

app = FastAPI(title="stemforge api-gateway")


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "api-gateway", "status": "ok"}
