from flask import Flask, request, send_file, jsonify
from PIL import Image
import io
import numpy as np
import pandas as pd
from pathlib import Path
import cv2

from ClipSearcher import CLIPSearcher, CLIPTagSearcher , create_clip_model, plot_images
from utils import pil_to_base64, base64_to_pil, tags_from_df, etsy_sites_from_df, get_etsy_queries, get_item_names, tags2string
import base64


pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 10)

#open products data
print('Loading data...')
# load dataframe with all products and embeddings
df_all = pd.read_parquet('./data/all_clip_embeddings.parquet')

#load dataframe with single tags and single tags embeddings
df_tags = pd.read_parquet('./data/all_single_tag_embeddings.parquet')
# keep unique tags
df_tags = df_tags.drop_duplicates(subset='Tags', keep='first')
# use only tags of popular products
df_popular_tags = df_tags[df_tags['NumReviews'] >= 100]

# Filter dataframe to have only popular items
# they must have 100 or more reviews
#df_popular = df_all[df_all['NumReviews'] >= 100]
df_popular = df_all[df_all['IsBestseller'] == 1]
print('all', df_all.shape, 'popular', df_popular.shape)

# set path of stored images
#root_path = Path('/vol/fob-vol6/mi13/pivillaa/code/stitches_workspace/etsy_dataset')
root_path = Path('/home/pico/code/stitches_workspace/etsy_dataset')

images_path = root_path / 'all_images'

# create clip model
clip_model = create_clip_model()
# create clip searchers for all and popular lists
print('Creating clip model...')
all_searcher = CLIPSearcher(df_all, clip_model=clip_model)
popular_searcher = CLIPSearcher(df_popular, clip_model=clip_model)
# create tags searcher (looks in database of single tags)
tag_searcher = CLIPTagSearcher(df_popular_tags, clip_model=clip_model)

# sets server for search in all the database or only popular items,, default all
search_mode = 'all' #all, popular, etsy(etsy search searches in all in disk and uses tags to create etsy query)
# sets the search space. search of queries for similar images, tags , or item name. default images
search_space = 'images'  #images,tags,names



app = Flask(__name__)

# gets an image and returns an image 
# cointaning similar products from the complete database
@app.route('/clip_query', methods=['POST'])
def process_clip_query():
    print('processing query ...')
    global search_mode
    global search_space
    #check if query is text or image
    if request.json['msg_type'] == 'image':
        img_str = request.json['image']
        # Convert the received base64 encoded string to a PIL image
        img = base64_to_pil(img_str)
        query = img
    else:
        txt = request.json['text']
        query = txt

    # use the right searcher for the search mode
    if (search_mode == 'tags') :
        # in tagssearch mode tagsdatabase is used
        # convert query to embeddings
        tag_searcher.gen_query(query)
        # search similar tags in embedding space
        df_result = tag_searcher.search_in_tags(15)
        # gets list of found tags
        tags = tags2string(df_result)
        # prepare other variables of response dict
        # no item names
        item_names = ''
        # no image
        processed_img_str = ''
        items_sites = ''
        etsy_queries = ''

    else:
        # use the right searcher for the search mode
        if (search_mode == 'all') :
            # convert query to embeddings and prepare it for querying
            all_searcher.gen_query(query)

            # search for similar
            if search_space == 'images':
                df_result = all_searcher.search_in_images(3)
            elif search_space == 'tags':
                df_result = all_searcher.search_in_tags(3)
            else:
                df_result = all_searcher.search_in_names(3)

            print('all', search_space)

        elif (search_mode == 'popular') or (search_mode == 'etsy'):
            # convert query to embeddings and prepare it for querying
            popular_searcher.gen_query(query)
            
            # search for similar
            if search_space == 'images':
                df_result = popular_searcher.search_in_images(3)
            elif search_space == 'tags':
                df_result = popular_searcher.search_in_tags(3)
            else:
                df_result = popular_searcher.search_in_names(3)

            print('popular', search_space)

        print(df_result)

        # Get item tags from dataframe
        tags = tags_from_df(df_result)
        # get item names
        item_names = get_item_names(df_result)
        print(item_names)

        # if search mode is etsy, return url for etsy query
        if search_mode == 'etsy':
            print('creating response url...')
            etsy_queries = get_etsy_queries(df_result)
            # set variables of response dictionary
            items_sites = ''
            # no image
            processed_img_str = ''
        
        else:
            etsy_queries = ''
            # Get items sites from dataframe
            items_sites = etsy_sites_from_df(df_result)

            # if not, return tags, and items images an urls
            print('creating response image...')

            # plot items in dataframe
            img_results = plot_images(df_result, images_path)
            # Convert the processed PIL image to a base64 encoded string
            processed_img_str = pil_to_base64(img_results)


    # Respond with the processed image as a base64 encoded string
    # and the string with tags
    print('ready to make response')
    response = {
        "status": "success",
        "item_names":  item_names,
        "search_mode": search_mode,
        "search_space": search_space,
        "items_sites" : items_sites,
        "etsy_queries" : etsy_queries,
        "tags" : tags,
        "processed_image": processed_img_str
    }
    return jsonify(response)

# sets server for search in all the database or only popular items
#all, popular
@app.route('/set_search_mode', methods=['POST'])
def set_search_mode():
    global search_mode    
    #changes search mode to all or only popular items in list
    if request.json['search_mode'] == 'all':
        search_mode = 'all'
        print('set search to all')
    elif request.json['search_mode'] == 'popular':
        search_mode = 'popular'
        print('set search to popular')
    elif request.json['search_mode'] == 'etsy':
        search_mode = 'etsy'
        print('set search to etsy')
    else:
        search_mode = 'tags'
        print('set search to tags')

    response = {
        "status": "success",
        "message": f"search mode set to {search_mode}",
    }
    return jsonify(response)

# sets the search space. search of queries for similar images, tags , or item name. default images
# images,tags,names
@app.route('/set_search_space', methods=['POST'])
def set_search_space():
    global search_space    
    #changes search space to images, tags , or item names
    if request.json['search_space'] == 'images':
        search_space = 'images'
        print('set search space to images')
    elif request.json['search_space'] == 'tags':
        search_space = 'tags'
        print('set search space to item tags')
    else:
        search_space = 'names'
        print('set search space to item names')

    response = {
        "status": "success",
        "message": f"search space set to {search_space}",
    }
    return jsonify(response)



'''
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
'''

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
