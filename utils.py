from datetime import datetime
from flask import jsonify

def getMessage(message):
    return jsonify({'message': message})

def forceDateTime(value):
    if isinstance(value, datetime):
        return datetime
    if isinstance(value, int):
        strDatetime = datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
        return datetime.strptime(strDatetime, '%Y-%m-%d %H:%M:%S')
    if isinstance(value, str):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')