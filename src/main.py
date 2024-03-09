from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from image_upload.router import router as image_router

origins = [
    "http://localhost",
    "http://localhost:8080",
]


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image_router)

# Wrap API with handler for deployment
handler = Mangum(app)


@app.get("/")
def home():
    return {"message": "Hello World!"}
