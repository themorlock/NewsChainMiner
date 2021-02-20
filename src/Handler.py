import flask
import jsonpickle
import requests
from src import main

app = flask.Flask(__name__)


@app.route('/new_article', methods=['POST'])
def new_article():
    article = jsonpickle.decode(flask.request.data.decode("utf-8"))
    if article.verify():
        main.current_articles.append(article)
        for peer_address in main.peer_addresses:
            requests.post('http://' + peer_address + ':' + str(main.PORT)
                          + '/new_article', data=jsonpickle.encode(article))


@app.route('/new_block', methods=['POST'])
def new_block():
    block = jsonpickle.decode(flask.request.data.decode("utf-8"))
    if main.chain.add_block(block):
        main.stop_mining_flag = True
        for peer_address in main.peer_addresses:
            requests.post('http://' + peer_address + ':' + str(main.PORT)
                          + '/new_block', data=jsonpickle.encode(block))


@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    return jsonpickle.encode(main.chain)


def handler_loop():
    app.run(host='0.0.0.0')
