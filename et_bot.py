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

with open("private_data.json", "r") as read_file:
    data = json.load(read_file)

TOKEN = data['telegram_token']

def start(update, context):
    update.message.reply_text("Hola")

def help(update, context):
    update.message.reply_text("""
    /start - dkjd
    /help - dhsd
    """)

def handle_message(update, context):
    update.message.reply_text("bbb")

def handle_photo(update, context):
    # Check if the message contains an image
    #if update.message.photo:

    # Save the image to disk
    #file.download('image.jpg')
    
    file_id = update.message.photo[-1].file_id
    file = context.bot.get_file(file_id)

    # Download the image as bytes
    image_bytes = BytesIO()
    file.download(out=image_bytes)
    image_bytes.seek(0)

    # Convert the bytes to a PIL image
    pil_image = Image.open(image_bytes)

    update.message.reply_text("Processing image. Please wait...")

    #send request to clip searcher
    url = 'http://127.0.0.1:5000/similar_im2im_all'
    img_str = pil_to_base64(pil_image)
    # send the image to the server
    payload = {"image": img_str}
    response = requests.post(url, json=payload)

    # Get the base64 encoded image data from the request
    img_str = response.json()['processed_image']
    r_im = base64_to_pil(img_str)
    #r_im.save('miimage.jpg')

    # Convert the resized image back to a byte stream
    img_byte_arr = BytesIO()
    r_im.save(img_byte_arr, format='JPEG')
    img_byte_arr.seek(0)  # Reset the file pointer to the beginning

    context.bot.send_photo(chat_id=update.message.chat_id, photo=img_byte_arr)


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


dp.add_handler(MessageHandler(Filters.text, handle_message))
dp.add_handler(MessageHandler(Filters.photo, handle_photo))
dp.add_handler(CommandHandler('sendimage', send_image))

updater.start_polling()
updater.idle()