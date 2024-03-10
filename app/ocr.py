import pathlib
import pytesseract
from PIL import Image

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "IMAGES"
img_path = IMG_DIR / "invoice.png"

img = Image.open(img_path)

preds = pytesseract.image_to_string(img)
preds = [p for p in preds.split("\n") if p]

print(preds)
