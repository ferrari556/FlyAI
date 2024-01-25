from fastapi import FastAPI
from routers.route import user
import uvicorn

app = FastAPI()

app.include_router(user)

@app.get('/')
def home():
    return {'msg' : 'Main'}

if __name__ == "__main__":
    uvicorn.run("main.py:app", host = "0.0.0.0", port = 8000, reload = True)

