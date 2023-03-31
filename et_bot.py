#from telegram.ext import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputFile
from io import BytesIO
import numpy as np

from utils import pil_to_base64, base64_to_pil
import requests
from skimage.io import imread
from PIL import Image

import requests
import json
import cv2
import os

from pathlib import Path
import datetime

# sets server for search in all the database or only popular items, default all
search_mode = 'all' #all, popular
# sets the search space. search of queries for similar images, tags , or item name. default images
search_space = 'images'  #images,tags,names


def save_im_timestamp(img, name, chat_id, folder_path):
    # Get the current date and time
    now = datetime.datetime.now()
    # Format the date and time as a string suitable for a file name
    date_time_string = now.strftime('%Y-%m-%d_%H-%M-%S')
    img.save(folder_path / (date_time_string + '_' + str(chat_id) + '_' + name +'.jpg'))

def save_text_timestamp(text, name, chat_id, folder_path):
    # Get the current date and time
    now = datetime.datetime.now()
    # Format the date and time as a string suitable for a file name
    date_time_string = now.strftime('%Y-%m-%d_%H-%M-%S')
    # create file name
    file_name = folder_path / (date_time_string + '_' + str(chat_id) + '_' + name +'.txt')
    # save string
    with open(file_name, "w") as text_file:
        text_file.write(text)

def set_search_mode(mode):
    # sets servers search mode
    global search_mode
    search_mode = mode

    #send request to clip searcher
    url = 'http://127.0.0.1:5000/set_search_mode'
    # send  text to the server
    payload = {"search_mode": mode}
    response = requests.post(url, json=payload)

    msg = response.json()['message']
    return msg


def set_search_space(mode):
    # sets servers search space
    global search_space
    search_space = mode

    #send request to clip searcher
    url = 'http://127.0.0.1:5000/set_search_space'
    # send  text to the server
    payload = {"search_space": mode}
    response = requests.post(url, json=payload)

    msg = response.json()['message']
    return msg


with open("private_data.json", "r") as read_file:
    data = json.load(read_file)

TOKEN = data['telegram_token']

def start(update, context):
    update.message.reply_text("Hola")

def help(update, context):
    update.message.reply_text("""
    /start - start
    /help - displays help
    /searchpopular - popular items search
    /searchall - all items search
    /searchetsy - etsy search
    /imagespace - images space search
    /tagspace - tags space search
    /namespace - names space search
    /searchmode - show search mode
    """)
    
def set_search_popular(update, context): 
    msg = set_search_mode('popular')
    update.message.reply_text(msg)

def set_search_all(update, context):
    msg = set_search_mode('all')
    update.message.reply_text(msg)

def set_search_etsy(update, context):
    msg = set_search_mode('etsy')
    update.message.reply_text(msg)

def set_image_space(update, context):
    msg = set_search_space('images')
    update.message.reply_text(msg)

def set_tag_space(update, context):
    msg = set_search_space('tags')
    update.message.reply_text(msg)

def set_name_space(update, context):
    msg = set_search_space('names')
    update.message.reply_text(msg)

def show_search_mode(update, context):
    global search_mode
    global search_space
    # displays current search configuration
    update.message.reply_text(f'search : {search_mode} in {search_space}')


def handle_message(update, context):
    global search_mode
    global search_space
    print(search_mode, search_space)

    # synchronize search mode and space with server
    set_search_mode(search_mode)
    set_search_space(search_space)

    # Get the message text
    message_text = update.message.text

    save_text_timestamp(message_text, 'q' ,str(update.message.chat_id), Path('../bot_images'))

    # do  regular query if search mode is not etsy
    if search_mode != 'etsy': #response.json()['search_mode'] != 'etsy':

        update.message.reply_text("Processing query. Please wait...")

        #send request to clip searcher
        url = 'http://127.0.0.1:5000/clip_query'
        # send  text to the server
        payload = {"msg_type":'text', "text": message_text}
        response = requests.post(url, json=payload)

        # send the received item tags to client
        tags = response.json()['tags']
        update.message.reply_text(tags)

        # Get the base64 encoded image data from the request
        img_str = response.json()['processed_image']
        r_im = base64_to_pil(img_str)
        # save answer image
        save_im_timestamp(r_im, 'a' ,str(update.message.chat_id), Path('../bot_images'))
        # Convert the resized image back to a byte stream
        img_byte_arr = BytesIO()
        r_im.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Reset the file pointer to the beginning

        # get etsy sites from response and add them as image captions
        etsy_sites = response.json()['items_sites']
        # send resulting image to client
        context.bot.send_photo(chat_id=update.message.chat_id, photo=img_byte_arr, caption=etsy_sites)

    else:
        # if it is in etsy mode , simply use message to generate etsy querie (move it to server!)
        #query_url = response.json()['etsy_queries']
        query_url = f"https://www.etsy.com/de-en/search?q={message_text.replace(' ','+')}&ref=search_bar"
        # save response
        save_text_timestamp(query_url, 'a' ,str(update.message.chat_id), Path('../bot_images'))
        # send message to telegram client
        update.message.reply_text(query_url)


def handle_photo(update, context):
    # Check if the message contains an image
    #if update.message.photo:
    # Save the image to disk
    #file.download('image.jpg')
    global search_mode
    global search_space
    print(search_mode, search_space)

    # synchronize search mode and space with server
    set_search_mode(search_mode)
    set_search_space(search_space)

      
    file_id = update.message.photo[-1].file_id
    file = context.bot.get_file(file_id)

    # Download the image as bytes
    image_bytes = BytesIO()
    file.download(out=image_bytes)
    image_bytes.seek(0)

    # Convert the bytes to a PIL image
    pil_image = Image.open(image_bytes)

    # save it to drive
    save_im_timestamp(pil_image, 'q' ,str(update.message.chat_id), Path('../bot_images'))

    update.message.reply_text("Processing query. Please wait...")

    #send request to clip searcher
    url = 'http://127.0.0.1:5000/clip_query'
    img_str = pil_to_base64(pil_image)
    # send the image to the server
    payload = {"msg_type":'image', "image": img_str}
    response = requests.post(url, json=payload)


    # if search mode is etsy, send only query url to telegram client
    if response.json()['search_mode'] == 'etsy':
        query_url = response.json()['etsy_queries']
        # save response
        save_text_timestamp(query_url, 'a' ,str(update.message.chat_id), Path('../bot_images'))
        # send message to telegram client
        update.message.reply_text(query_url)

    else:
        # send the received item tags to telegram client
        tags = response.json()['tags']
        update.message.reply_text(tags)

        # Get the base64 encoded image data from the request
        img_str = response.json()['processed_image']
        r_im = base64_to_pil(img_str)
        # save answer image
        save_im_timestamp(r_im, 'a' ,str(update.message.chat_id), Path('../bot_images'))
        # Convert the resized image back to a byte stream
        img_byte_arr = BytesIO()
        r_im.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)  # Reset the file pointer to the beginning

        # get etsy sites from response and add them as image captions
        etsy_sites = response.json()['items_sites']
        # send resulting image to client
        context.bot.send_photo(chat_id=update.message.chat_id, photo=img_byte_arr,caption=etsy_sites)

    

'''
# Define a function to send images to the user
def send_image(update, context):
    # Read the image from disk
    if os.path.exists('image.jpg'):
        with open('image.jpg', 'rb') as f:
            # Send the image as a photo using the bot's send_photo() method
            update.message.reply_photo(photo=f)
    else:
        # Send an error message if the image file does not exist
        update.message.reply_text('No image found.')
'''

'''
# assume you have a PIL image object named pil_image
# convert the PIL image object to a byte stream
with io.BytesIO() as output:
    pil_image.save(output, format='PNG')
    content = output.getvalue()

# create an InputFile object from the byte stream
photo = InputFile(io.BytesIO(content), filename='my_photo.png')

# send the photo using the bot object
bot.send_photo(chat_id=chat_id, photo=photo)

updater = Updater(token='YOUR_TOKEN_HERE', use_context=True)
bot = updater.bot

# send an image from file
    bot.send_photo(chat_id=chat_id, photo=open('path/to/image.jpg', 'rb'))
    # send an image from a PIL Image object
    pil_image = Image.open('path/to/image.jpg')
    image_file = io.BytesIO()
    pil_image.save(image_file, 'JPEG')
    image_file.seek(0)
    bot.send_photo(chat_id=chat_id, photo=image_file)


'''



updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("help", help))
dp.add_handler(CommandHandler('searchpopular', set_search_popular))
dp.add_handler(CommandHandler('searchall', set_search_all))
dp.add_handler(CommandHandler('searchetsy', set_search_etsy))
dp.add_handler(CommandHandler('imagespace', set_image_space))
dp.add_handler(CommandHandler('tagspace', set_tag_space))
dp.add_handler(CommandHandler('namespace', set_name_space))
dp.add_handler(CommandHandler('searchmode', show_search_mode))

dp.add_handler(MessageHandler(Filters.text, handle_message))
dp.add_handler(MessageHandler(Filters.photo, handle_photo))


updater.start_polling()
updater.idle()