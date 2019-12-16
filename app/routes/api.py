from flask import jsonify

from app import app

@app.route('/versions')
def versions():
    return jsonify({
        'osu': 1,
        'pusher': 3,
    })
