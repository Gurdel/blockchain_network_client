from hashlib import sha256
import json
from transaction import Transaction

from typing import List


class Block(dict):
    """
    Клас для збереження блоків у блокчейні
    """
    NONCE = "0"  # Необхідний заголовок хешу блоку для PoW

    def __init__(self, index: int, time: float, transactions: List[Transaction], proof: int, prev_hash: str):
        """
        Конструктор класу
        :param index: порядковий номер блоку
        :param time: час створення блоку
        :param transactions: транзакції, які зберігаються в блоці
        :param proof: доказ роботи алгоритмом PoW
        :param prev_hash: хеш попереднього блоку
        """
        if transactions is None:
            transactions = []
        block = {
            'index': index,
            'timestamp': time,
            'proof': proof,
            'transactions': transactions,
            'merkle': self.merkle(transactions),  # хеш транзакцій, отриманий обрахунком дерева Меркла
            'previous_hash': prev_hash,
        }
        block['hash'] = self.get_block_hash()  # хеш даного блоку
        dict.__init__(self, **block)

    def get_block_hash(self) -> str:
        """
        Обраховує та повертає хеш блоку, використовуючи хеш-функцію sha256
        :return: значення хешу блоку
        """
        self['hash'] = ''
        block_string = json.dumps(self, sort_keys=True).encode()
        self['hash'] = sha256(block_string).hexdigest()
        return self['hash']

    def merkle(self, transaction: List[Transaction]) -> str:
        """
        Обраховує та повертає дерево Меркла транзакцій блоку
        :param transaction: транзакції, які зберігаються в блоці
        :return: значення хешу кореня дерева Меркла
        """
        if not transaction:
            return ''

        def tree(hashes: List[str]) -> str:
            """
            Рекурсивна функція обрахунку хешу кореня дерева Меркла
            :param hashes: масив хешів транзакцій
            :return: хеш кореня дерева Меркла
            """
            count = len(hashes)
            if count == 1:
                return hashes[0]
            return sha256(tree(hashes[:count // 2]).encode() + tree(hashes[count // 2:]).encode()).hexdigest()

        transaction_hashes = [tr.get_transaction_hash() for tr in transaction]
        return tree(transaction_hashes)

    def validate_proof(self) -> bool:
        """
        Перевірка коректності знайденого доказу роботи методом PoW
        :return: True, якщо доказ роботи знайдений правильно (хеш блоку починається з NONCE), інакше False
        """
        block_hash = Block.get_block_hash(self)
        return block_hash.startswith(Block.NONCE)
