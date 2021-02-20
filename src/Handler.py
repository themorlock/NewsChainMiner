import flask
import jsonpickle
import requests
import json
import Article
import Block
import main

app = flask.Flask(__name__)


@app.route('/new_article', methods=['POST'])
def new_article():
    json_dict = json.loads(flask.request.data.decode("utf-8"))
    json_dict.update({"py/object":"Article.Article"})
    article = jsonpickle.loads(json.dumps(json_dict))
    #article = jsonpickle.decode(flask.request.data.decode("utf-8"), classes=Article.Article)
    if article.verify():
        main.current_articles.append(article)
        for peer_address in main.peer_addresses:
            requests.post('http://' + peer_address + ':' + str(main.PORT)
                          + '/new_article', data=jsonpickle.encode(article))
    return 'Recieved'


@app.route('/new_block', methods=['POST'])
def new_block():
    json_dict = json.loads(flask.request.data.decode("utf-8"))
    json_dict.update({"py/object":"Block.Block"})
    block = jsonpickle.loads(json.dumps(json_dict))
    #block = jsonpickle.decode(flask.request.data.decode("utf-8"), classes=Block.Block)
    if main.chain.add_block(block):
        main.stop_mining_flag = True
        for peer_address in main.peer_addresses:
            requests.post('http://' + peer_address + ':' + str(main.PORT)
                          + '/new_block', data=jsonpickle.encode(block))
    return 'Recieved'


@app.route('/get_blockchain', methods=['GET'])
def get_blockchain():
    return jsonpickle.encode(main.chain)


def handler_loop():
    app.run(host='0.0.0.0')
