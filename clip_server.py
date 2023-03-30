from flask import Flask, request, send_file
from PIL import Image
import io
import numpy as np
import cv2



app = Flask(__name__)

@app.route('/process_image', methods=['POST'])
def process_image():
    # receive the image from the client
    file = request.files['image'].read()
    
    # convert the image to a numpy array
    image = np.frombuffer(file, np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    
    # convert the image to black and white
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, bw = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # convert the black and white image to a PIL image
    pil_image = Image.fromarray(bw)
    
    # save the image to a buffer
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    
    # convert the buffer to bytes
    buffer.seek(0)
    output = buffer.getvalue()
    
    # send the black and white image back to the client
    return output
    
if __name__ == '__main__':
    app.run()











'''
app = Flask(__name__)

# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload():
    # Get image file from request
    file = request.files['image']
    
    # Convert image to PIL format
    img = Image.open(io.BytesIO(file.read()))
    img.save('testim.jpg')
    # Process image...
    
    # Return response
    return 'Image received'

# Download endpoint
@app.route('/download')
def download():
    # Open image file
    img = Image.open('./test_image.jpg')
    
    # Convert image to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    # Return response with image bytes
    return send_file(img_bytes, mimetype='image/jpeg')


if __name__ == '__main__':
    #app.run(host='0.0.0.0',port=8090)
    app.run()
'''