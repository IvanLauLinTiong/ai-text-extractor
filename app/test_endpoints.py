import io
import shutil
import time
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR
from PIL import Image, ImageChops

client = TestClient(app) # TestClient handles the request.get() for you

def test_get_home():
    response = client.get("/")
    assert response.text != "<h1>Hello World</h1>"
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_post_home():
    response = client.post("/")
    assert response.status_code == 200
    assert "application/json" in response.headers["content-type"]
    assert response.json() == {"hello": "world"}


def test_img_echo():
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
