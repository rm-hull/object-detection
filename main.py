import os
import logging
from typing import Generator
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine, select
from inference import Inferencer

from models.file import File
from video import video_frames
from walk import recursive_walk


load_dotenv()
logger = logging.getLogger()
engine = create_engine("sqlite:////app/data/objects.db", echo=True,
                       connect_args={"check_same_thread": False})

app = FastAPI(title="Object Detection")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator:
    session = None
    try:
        with Session(engine) as session:
            yield session
    finally:
        if session is not None:
            session.close()


@app.get("/collect")
async def collect(request: Request, session: Session = Depends(get_session)):
    directory = "/app/files"

    async def event_generator():
        for filename in recursive_walk(directory):
            if await request.is_disconnected():
                logger.debug("Request disconnected")
                break

            file = File(filename=filename, scanned=None)
            session.add(file)
            yield {
                "event": "new_file",
                "id": file.id,
                "data": file.filename,
            }

        session.commit()

    return EventSourceResponse(event_generator())


@app.get("/detect")
async def detect(request: Request, session: Session = Depends(get_session)):

    inferencer = Inferencer(
        model=os.getenv('MODEL_FILE'),
        labels=os.getenv('LABELS_FILE')
    )

    async def event_generator():
        statement = select(File).where(File.scanned == None)
        for file in session.exec(statement).all():

            yield {
                "event": "file",
                "id": file.id,
                "data": file.filename,
            }

            for count, frame in enumerate(video_frames(file.filename)):

                if await request.is_disconnected():
                    logger.debug("Request disconnected")
                    break

                objs = inferencer.detect(frame)
                if objs:
                    yield {
                        "event": "frame",
                        "id": count,
                        "data": objs
                    }

    return EventSourceResponse(event_generator())
