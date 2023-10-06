
from flask import Flask, jsonify
from modules.email_handler import check_emails

app = Flask(__name__)


@app.route('/check-emails', methods=['GET'])
def trigger_check_emails():
    result = check_emails()
    return jsonify(result)


if __name__ == '__main__':
    app.run()
