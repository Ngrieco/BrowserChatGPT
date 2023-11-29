from flask import Flask, jsonify, request

from browserchatgpt import BrowserChatGPT

app = Flask(__name__)
browserchatgpt = BrowserChatGPT()


@app.route("/api/url", methods=["GET"])
# @app.route("/api/url", methods=["PUT"])
def url_endpoint():
    url = request.args.get("url")

    browserchatgpt.submit_url(url)
    response = {"success": True}

    return jsonify(response)


@app.route("/api/query", methods=["GET"])
def query_endpoint():
    query = request.args.get("query")
    print("Query ", query)

    response = browserchatgpt.query_llm(query)
    response = {"response": response}

    return jsonify(response)


"""
import logging
logging.basicConfig(filename='error.log', level=logging.DEBUG)

# Add a logging handler to capture 403 errors
file_handler = logging.FileHandler('error.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
app.logger.addHandler(file_handler)

# Route that triggers a 403 Forbidden error
@app.route('/forbidden')
def trigger_forbidden():
    app.logger.error('403 Forbidden error occurred')  # Log the 403 error
    return "Forbidden", 403
"""

if __name__ == "__main__":
    app.run(debug=True)
