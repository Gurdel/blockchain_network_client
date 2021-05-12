"""
Виконавчий файл клієнта мережі блокчейн
"""
from argparse import ArgumentParser
from uuid import uuid4
from flask import Flask, jsonify, request
import random

from blockchain import Blockchain

app = Flask(__name__)
user_id = str(uuid4()).replace('-', '')  # Генерує ідетифікатор клієнта
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    """
    Майнінг нового блоку
    :return: змайнений блок
    """

    # Додає транзакцію з винагородою для користувача за змайнений блок
    blockchain.new_transaction(
        sender="0",  # Вказує, що це винагорода за майнінг
        recipient=user_id,
        quantity=1,
    )

    # Пошук значення доказу роботи для алгоритма PoW
    proofed_block = None
    while proofed_block is None:
        proof = random.randint(0, 99999999999999999999999999999999999)
        proofed_block = blockchain.proof_of_work(proof)

    blockchain.new_block(proofed_block)

    return jsonify(proofed_block)


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    Створює нову транзакцію
    :return: Повідомлення з номером блоку, в який буде додано транзакцію
    """
    transaction = request.get_json()
    index = blockchain.new_transaction(transaction['sender'], transaction['recipient'], transaction['amount'])
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response)


@app.route('/chain', methods=['GET'])
def chain():
    """
    Метод для отримання ланцюга блоків користувача
    :return: ланцюг блоків та його довжина
    """
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response)


@app.route('/nodes/add', methods=['POST'])
def add_nodes():
    """
    Додає адреси інших користувачів до списку адрес користувача
    :return: повідомлення зі списком усіх адрес інших користувачів
    """
    nodes = request.get_json()

    nodes = nodes.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes"

    for node in nodes:
        blockchain.add_node(node)

    response = {
        'message': 'New nodes added',
        'nodes': list(blockchain.nodes),
    }
    return jsonify(response)


@app.route('/chain/update', methods=['GET'])
def update_chain():
    """
    Знаходить головний ланцюг (валідний та найдовший) у мережі
    :return: ланцюг блоків після оновлення
    """
    replaced = blockchain.find_main_chain()

    if replaced:
        response = {
            'message': 'Chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Chain is main',
            'chain': blockchain.chain
        }

    return jsonify(response)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()

    port = args.port
    app.run(host='127.0.0.1', port=port)
