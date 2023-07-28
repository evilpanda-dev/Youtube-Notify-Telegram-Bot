import os
import xml.etree.ElementTree as ET

import pymongo
import telebot
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/callback": {"origins": "*"}})

# Load environment variables from .env file
load_dotenv()

# Connect to the MongoDB database and the password is stored in the environment variable
mongo_connection_string = os.environ.get("MONGO_CONNECTION")
bot = telebot.TeleBot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))
mongo_client = pymongo.MongoClient(mongo_connection_string)
db = mongo_client["ytNotify"]
collection = db["Youtube Notifications"]

# Function to get the video URL from the video ID
def get_video_url(video_id):
    return f"https://www.youtube.com/watch?v={video_id}"

# Function to check if 'live' is in the video_title
def is_live(video_title):
    return True if 'live' in video_title.lower() else False

@app.route('/callback', methods=['POST', 'GET'])
def callback():
    if request.method == 'POST':
        # Process POST request
        data = request.data
        root = ET.fromstring(data)

        # Define the namespace used in the XML
        ns = {'yt': 'http://www.youtube.com/xml/schemas/2015'}
        try:
            # Extract the video ID and channel ID from the entry element
            video_id = root.find(".//yt:videoId", namespaces=ns).text
            channel_id = root.find(".//yt:channelId", namespaces=ns).text

            # Extract video title from the entry element
            entry_element = root.find(".//{http://www.w3.org/2005/Atom}entry", namespaces=ns)
            video_title = entry_element.find(".//{http://www.w3.org/2005/Atom}title").text

            # Check if the video ID is already in the database
            existing_record = collection.find_one({"video_id": video_id})

            if existing_record:
                # Video ID already exists in the database, do not insert a duplicate
                return 'Video ID already exists in the database.', 200

            # Store the data in MongoDB
            video_data = {
                'channel_id': channel_id,
                'video_id': video_id,
                'video_title': video_title
            }
            collection.insert_one(video_data)

            # Check if the video title contains 'live' (case-insensitive)
            if is_live(video_title):
                # Send a message about the scheduled livestream
                live_url = get_video_url(video_id)
                bot.send_message(chat_id=os.environ.get("TELEGRAM_GROUP_CHAT_ID"),
                                 text=f"Va astept la un nou LIVE!\n{live_url}")
            else:
                # Send a message about the new video
                video_url = get_video_url(video_id)
                bot.send_message(chat_id=os.environ.get("TELEGRAM_GROUP_CHAT_ID"),
                                 text=f"Videoclip nou pe canal!\n{video_url}")

            # Return the event data as JSON response
            response_data = {
                'channel_id': channel_id,
                'video_id': video_id,
                'video_title': video_title
            }

            return jsonify(response_data)
        except AttributeError:
            return 'Video ID or channel ID not found in the XML.', 400

    elif request.method == 'GET' and request.args.get('hub.challenge'):
        # Process GET request with 'hub.challenge'
        return 'Successfully subscribed!', 200

    return 'Invalid request.'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT'), ssl_context='adhoc')
