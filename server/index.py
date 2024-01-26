from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )