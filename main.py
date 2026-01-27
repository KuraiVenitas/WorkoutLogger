from fastapi import FastAPI

app = FastAPI()

@app.get("/")

@app.get("/")
def root():
        return {"status": "ok"}