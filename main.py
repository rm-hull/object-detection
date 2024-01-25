from fastapi import FastAPI, APIRouter


router = APIRouter()


@router.get("/")
def hello():
    return {
        "hello": 1,
        "world": 2
    }


app = FastAPI(title="Object Detection")
app.include_router(router)