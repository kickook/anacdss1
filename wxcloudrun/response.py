from flask import jsonify


def success(data=None, message="ok"):
    payload = {"success": True, "message": message, "data": data}
    return jsonify(payload)


def error(message, status=400, data=None):
    payload = {"success": False, "message": message, "data": data}
    return jsonify(payload), status
