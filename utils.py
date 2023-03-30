
from PIL import Image
import io
import base64

def pil_to_base64(pil_im):
    # Convert the PIL image to a base64 encoded string
    buffer = io.BytesIO()
    pil_im.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return img_str

def base64_to_pil(img_str):
    # Convert the base64 encoded string back to a PIL image
    img_data = base64.b64decode(img_str)
    pil_img = Image.open(io.BytesIO(img_data))
    return pil_img