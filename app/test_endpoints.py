import shutil
import time
from fastapi.testclient import TestClient
from app.main import app, BASE_DIR, UPLOAD_DIR

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
        response = client.post("/img-echo", files={"file": open(path, "rb")})
        assert response.status_code == 200
        fext = str(path.suffix).replace(".", "")
        if fext == "txt":
            assert "text/plain" in response.headers["content-type"]
        else:
            assert fext in response.headers["content-type"]
    # time.sleep(3)
    shutil.rmtree(UPLOAD_DIR)
