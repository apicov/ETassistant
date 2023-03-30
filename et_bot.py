#from telegram.ext import *
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InputFile
from io import BytesIO
import numpy as np

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


    f = BytesIO(file.download_as_bytearray())
    file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)

    img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    #img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    #img = cv2.resize(img, (32, 32), interpolation=cv2.INTER_AREA)

    cv2.imwrite('test_image.jpg', img)
    # Convert the OpenCV image to a PIL Image object
    #pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    
    update.message.reply_text("me ha llegao la imagen")

    # assume 'photo' is the PhotoSize object received from Telegram
    #file_bytes = photo.get_file().download_as_bytearray()
    # convert the byte data into a numpy array
    #np_array = np.frombuffer(file_bytes, np.uint8)
    # convert the numpy array into a PIL image
    #pil_img = Image.open(BytesIO(np_array))


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