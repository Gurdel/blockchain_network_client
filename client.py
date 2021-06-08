"""
Виконавчий файл клієнта мережі блокчейн
"""
from argparse import ArgumentParser
from uuid import uuid4
from flask import Flask, jsonify, request
import random
from Crypto.PublicKey import RSA
from hashlib import sha512

from blockchain import Blockchain

app = Flask(__name__)
user_id = str(uuid4()).replace('-', '')  # Генерує ідетифікатор клієнта
print('user_id: ', user_id)
keyPair = RSA.generate(bits=1024)
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
        proof = random.randint(10000000000000000000000000000000000, 99999999999999999999999999999999999)
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
    message = transaction['message']

    msg_hash = int.from_bytes(sha512(str.encode(message)).digest(), byteorder='big')
    signature = pow(msg_hash, keyPair.d, keyPair.n)

    index = blockchain.new_transaction(transaction['sender'], transaction['recipient'], transaction['amount'], message,
                                       signature, (keyPair.e, keyPair.n))
    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response)


@app.route('/transactions/check', methods=['POST'])
def check_signature():
    """
    Перевіряє підпис повідомлення
    :return: Результат перевірки
    """
    transaction = request.get_json()
    message = str.encode(transaction['message'])
    key = transaction['key']
    signature = transaction['signature']

    msg_hash = int.from_bytes(sha512(message).digest(), byteorder='big')
    sign_hash = pow(signature, key[0], key[1])

    response = {'msg_hash': f'{msg_hash}', 'sign_hash': f'{sign_hash}', 'valid': msg_hash == sign_hash}
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
