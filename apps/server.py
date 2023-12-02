from flask import Flask, jsonify, request

from browserchatgpt import BrowserChatGPT

app = Flask(__name__)

use_robot_txt = False
browserchatgpt = BrowserChatGPT(use_robot_txt)

@app.route("/api/url", methods=["GET"])
def url_endpoint():
    url = request.args.get("url")

    try:
        browserchatgpt.submit_url(url)
        response = {"success": True}
    except Exception:
        response = {"success": False}

    return jsonify(response)


@app.route("/api/query", methods=["GET"])
def query_endpoint():
    query = request.args.get("query")
    print("Query ", query)

    response = browserchatgpt.query_llm(query)
    response = {"response": response}

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
