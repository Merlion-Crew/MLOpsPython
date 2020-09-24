from flask import Flask, request, make_response, jsonify
import main

app = Flask(__name__)
main.init()

@app.route("/")
def hello():
    return "Hello World!"

@app.route('/score', methods=['POST'])
def score_realtime():

    print(request.get_json()['data'])

    #require request data in json format
    if 'Content-Type' not in request.headers or request.headers['Content-Type'] != 'application/json':
        return make_response(
            'Expects Content-Type to be application/json!',
            415
        )

    response = main.run(request.get_json()['data'], request.headers)
    headers = {"Content-Type": "application/json"}
    return make_response(
        jsonify(response),
        200,
        {"Content-Type": "application/json"}
    )
