from flask import (jsonify)

def returner(answer):
    responseObj = {"update" : answer}

    response = jsonify(responseObj)
    response.headers.add('Access-Control-Allow-Origin', '*')

    return jsonify(responseObj)