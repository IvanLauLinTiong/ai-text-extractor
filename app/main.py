import io
import pathlib
import uuid
import pytesseract
from functools import lru_cache
from fastapi import (
    FastAPI,
    Header,
    HTTPException,
    Depends,
    Request,
    File,
    UploadFile
)
from fastapi.responses import FileResponse, HTMLResponse # HTMLResponse -> expect return HTML string
from fastapi.templating import Jinja2Templates
from PIL import Image
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_auth_token: str
    debug: bool = False
    echo_active: bool = False
    app_auth_token_prod: str = None
    skip_auth: bool = False

    class Config:
        env_file = ".env"

@lru_cache
def get_settings():
    return Settings()

# DEBUG = get_settings().debug # even match with uppercase DEBUG that defined in .env
# print(f"{DEBUG=}")

BASE_DIR = pathlib.Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "uploaded"

app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@app.get("/", response_class=HTMLResponse)
def home_view(request: Request, settings: Settings = Depends(get_settings)):
    return templates.TemplateResponse("home.html", context={"request": request, "name": "Ivan"})


def verify_auth(authorization = Header(None), settings:  Settings = Depends(get_settings)):
    """
    Authorization: Bearer <token>
    {"authorization": "Bearer <token>"}
    """
    if settings.debug and settings.skip_auth:
        return

    if authorization is None:
        raise HTTPException(detail="Invalid authorization", status_code=401)

    _, token = authorization.split()

    if token != settings.app_auth_token:
        raise HTTPException(detail="Invalid authorization", status_code=401)




@app.post("/")
async def prediction_view(
    file: UploadFile = File(...),
    authorization = Header(None),
    settings: Settings = Depends(get_settings)
):
    verify_auth(authorization, settings)

    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)

    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)

    preds = pytesseract.image_to_string(img)
    predictions = [p for p in preds.split("\n") if p]

    return {"result": predictions, "original": preds}


@app.post("/img-echo/",  response_class=FileResponse)
async def img_echo_view(file: UploadFile = File(...),  settings: Settings = Depends(get_settings)): # load the file in async manner

    if not settings.echo_active:
        raise HTTPException(detail="Invalid endpoint", status_code=400)

    UPLOAD_DIR.mkdir(exist_ok=True)
    bytes_str = io.BytesIO(await file.read())
    try:
        img = Image.open(bytes_str)
    except:
        raise HTTPException(detail="Invalid image", status_code=400)

    fname = pathlib.Path(file.filename)
    fext = fname.suffix # .jpg, .txt
    dest = UPLOAD_DIR / f"{uuid.uuid1()}{fext}"

    # save the file into dest
    # with open(str(dest), "wb") as out:
    #     out.write(bytes_str.read())
    img.save(dest)

    return dest
