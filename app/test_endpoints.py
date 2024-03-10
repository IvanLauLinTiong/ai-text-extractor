import io
import shutil
import time
from fastapi.testclient import TestClient
from app.main import app, get_settings, BASE_DIR, UPLOAD_DIR
from PIL import Image, ImageChops

client = TestClient(app) # TestClient handles the request.get() for you

def test_get_home():
    response = client.get("/")
    assert response.text != "<h1>Hello World</h1>"
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_post_invalid_file_upload_error():
    response = client.post("/")
    assert response.status_code == 422
    assert "application/json" in response.headers["content-type"]


def test_prediction_upload_missing_header():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/",
            files={"file": open(path, "rb")},
        )

        assert response.status_code == 401


def test_prediction_upload():
    img_saved_path = BASE_DIR / "images"
    settings = get_settings()
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/",
            files={"file": open(path, "rb")},
            headers={"Authorization": f"JWT {settings.app_auth_token}"}
        )

        if img is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            data = response.json()
            assert len(data.keys()) == 2


def test_img_upload():
    img_saved_path = BASE_DIR / "images"
    for path in img_saved_path.glob("*"):
        try:
            img = Image.open(path)
        except:
            img = None

        response = client.post("/img-echo", files={"file": open(path, "rb")}) # here open file is equivalent to file uploading
        if img is None:
            assert response.status_code == 400
        else:
            assert response.status_code == 200
            r_stream = io.BytesIO(response.content)
            echo_img = Image.open(r_stream)
            diff = ImageChops.difference(echo_img, img).getbbox()
            assert diff is None
    # time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)
