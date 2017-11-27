from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/ping", methods=["Get"])
def ping_pong():
    return jsonify({
        "status": "success",
        "message": "pong!"
    })