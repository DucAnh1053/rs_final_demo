from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import pickle
from bson import ObjectId
from pymongo import MongoClient
import implicit
from gridfs import GridFS

import json
import base64
app = Flask(__name__)
CORS(app)


# Connect to MongoDB
client = MongoClient(
    'mongodb+srv://takhanhlyt66:Vly.19952003@cluster0.czn0pgn.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['dtu']
grid_fs = GridFS(db)


@app.route('/openVideo/<qid>', methods=['GET'])
def open_video(qid):
    try:
        video_object_id = ObjectId(qid)
        file = grid_fs.find_one({'_id': video_object_id})
        if not file:
            return jsonify({'error': 'Video file not found.'}), 404

        range_header = request.headers.get('Range', None)
        if not range_header:
            # If no Range header, stream the whole file
            video_stream = grid_fs.get(video_object_id)
            response = Response(video_stream, content_type='video/mp4')
            response.headers['Content-Length'] = file.length
            return response
        else:
            # Handle Range header for partial content streaming
            start, end = range_header.replace('bytes=', '').split('-')
            start = int(start)
            end = int(end) if end else file.length - 1

            video_stream = grid_fs.get(video_object_id)
            video_stream.seek(start)

            chunk_size = end - start + 1
            data = video_stream.read(chunk_size)
            
            response = Response(data, status=206, content_type='video/mp4')
            response.headers['Content-Range'] = f'bytes {start}-{end}/{file.length}'
            response.headers['Accept-Ranges'] = 'bytes'
            response.headers['Content-Length'] = str(chunk_size)
            return response
    except Exception as e:
        return jsonify({'error': 'Internal Server Error'}), 500


    

if __name__ == '__main__':
    app.run(port=8000, debug=True)
