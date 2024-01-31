import os
import cv2
import logging
from typing import Generator
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine, select
from inference import Inferencer
from datetime import datetime

from models.file import File
from models.frame import Frame
from models.object import Object
from video import video_frames
from walk import recursive_walk


load_dotenv()
logger = logging.getLogger()
engine = create_engine(
    "sqlite:////app/data/objects.db",
    echo=False,
    connect_args={"check_same_thread": False},
)

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
        model=os.getenv("MODEL_FILE"), labels=os.getenv("LABELS_FILE")
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
                if count % 10 > 0:
                    continue

                if await request.is_disconnected():
                    logger.debug("Request disconnected")
                    break

                detected_objects = inferencer.detect(frame)
                if detected_objects:
                    annotated = inferencer.append_objs_to_img(frame, detected_objects)

                    retval, jpeg_bytes = cv2.imencode(".jpg", annotated)
                    if retval:
                        frame = Frame(
                            file_id=file.id,
                            frame_count=count,
                            image=jpeg_bytes.tobytes(),
                        )
                    else:
                        frame = Frame(file_id=file.id, frame_count=count, image=None)

                    session.add(frame)

                    for obj in detected_objects:
                        label = inferencer.label(obj.id)
                        object = Object(
                            file_id=file.id,
                            frame_id=frame.id,
                            label=label,
                            score=obj.score,
                        )
                        session.add(object)

                    yield {
                        "event": "frame",
                        "id": frame.id,
                        "data": inferencer.as_dict_array(detected_objects),
                    }


                file.scanned = datetime.utcnow()
                session.add(file)
                session.commit()

    return EventSourceResponse(event_generator())

@app.get("/frame/{frame_id}", response_class=Response)
async def frame(frame_id: str, session: Session = Depends(get_session)):
    frame = session.get(Frame, frame_id)
    if not frame:
        raise HTTPException(status_code=404, detail="Frame not found")
    return Response(content=frame.image, media_type="image/jpeg")