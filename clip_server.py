from flask import Flask, request, send_file, jsonify
from PIL import Image
import io
import numpy as np
import pandas as pd
from pathlib import Path
import cv2

from ClipSearcher import CLIPSearcher , plot_images
from utils import pil_to_base64, base64_to_pil, tags_from_df
import base64


pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 10)

#open products data
print('Loading data...')
df = pd.read_parquet('./data/all_clip_embeddings.parquet')

# Filter dataframe to have only popular items
# they must have 100 or more reviews
df = df[df['NumReviews'] >= 100]
print('n items', df.shape)

# set path of stored images
root_path = Path('/vol/fob-vol6/mi13/pivillaa/code/stitches_workspace/etsy_dataset')
images_path = root_path / 'all_images'

# create clip searcher with df
print('Creating clip model...')
searcher = CLIPSearcher(df)



app = Flask(__name__)

# gets an image and returns an image 
# cointaning similar products from the complete database
@app.route('/clip_query', methods=['POST'])
def process_clip_query():
    #check if query is text or image
    if request.json['msg_type'] == 'image':
        img_str = request.json['image']
        # Convert the received base64 encoded string to a PIL image
        img = base64_to_pil(img_str)
        query = img
    else:
        txt = request.json['text']
        query = txt
    
    # convert query to embeddings and prepare it for querying
    searcher.gen_query(query)
    # search for similar images
    df_result = searcher.search_in_images(3)
    print(df_result)

    # plot items in dataframe
    img_results = plot_images(df_result, images_path)
    # Convert the processed PIL image to a base64 encoded string
    processed_img_str = pil_to_base64(img_results)

    # Get item tags from dataframe
    tags = tags_from_df(df_result)

    # Respond with the processed image as a base64 encoded string
    # and the string with tags
    response = {
        "status": "success",
        "message": "Image received and processed successfully",
        "tags" : tags,
        "processed_image": processed_img_str
    }
    return jsonify(response)







    # save the image to a buffer
    buffer = io.BytesIO()
    img_results.save(buffer, format='PNG')
    # convert the buffer to bytes
    buffer.seek(0)
    output = buffer.getvalue()
    
    
    return output





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


def main():
    app.run()


if __name__ == '__main__':
    main()











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