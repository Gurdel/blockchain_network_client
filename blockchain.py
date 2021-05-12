from time import time
import requests
from typing import List

from block import Block
from transaction import Transaction
from node import Node


class Blockchain:
    """
    Клас для збереження ланцюга блокчейну
    """
    def __init__(self):
        """
        Конструктор класу
        """
        self.current_transactions = []  # Транзакції, які мають бути додані до наступного блоку
        self.chain = []  # Ланцюг блоків
        self.nodes = []  # Список адрес інших користувачів мережі

        # Створення початкового (генезисного) блоку
        self.new_block(Block(index=0, time=time(), transactions=[], proof=0, prev_hash=Block.NONCE))

    def add_node(self, link: str):
        """
        Додає нову адресу користувача до списку
        :param link: адреса користувача
        """
        self.nodes.append(Node(link))

    def validate_chain(self, chain: List[Block]) -> bool:
        """
        Перевіряє коректність ланцюга блоків. Критерії:
        - правильно вказаний хеш попереднього блоку
        - хеш даного блоку обрахований вірно
        - доказ роботи знайдено правильно
        :param chain: ланцюг блоків для перевірки
        :return: True, якщо ланюг коректний, інакше False
        """
        for i in range(1, len(chain)):
            print(f'{chain[i - 1]}')
            print(f'{chain[i]}')
            print("\n-----------\n")

            if chain[i]['previous_hash'] != chain[i - 1]['hash'] or \
                    chain[i]['hash'] != Block.get_block_hash(chain[i]) or \
                    not Block.validate_proof(chain[i]):
                return False

        return True

    def find_main_chain(self) -> bool:
        """
        Пошук найдовшого коректного ланцюга блоків у мережі
        :return: True, якщо знайдено ланцюг, довший за наший, інакше False
        """
        new_chain = None
        max_chain_length = len(self.chain)

        # Перевіряємо ланцюги блоків інших користувачів
        for node in self.nodes:
            response = requests.get(f'http://{node["link"]}/chain')  # Запит на отримання ланцюга іншого користувача
            length = response.json()['length']
            chain = response.json()['chain']

            # Якщо ланцюг валідний та має більшу довжину, замінюємо наший ланцюг
            if length > max_chain_length and self.validate_chain(chain):
                max_chain_length = length
                new_chain = chain

        # Зміна нашого ланцюга на довший
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, block: Block) -> Block:
        """
        Додає новий блок до нашого ланцюга
        :param block: змайнений блок
        :return: цей же блок
        """
        # Транзакції підтверджені, очищаємо список транзакцій
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender: str, recipient: str, quantity: float):
        """
        Додає нову транзакцію
        :param sender: відправник
        :param recipient: отримувач
        :param quantity: кількість умовних одиниць
        :return: індекс блоку, до якого буде додана транзакція
        """
        self.current_transactions.append(
            Transaction(
                sender=sender,
                recipient=recipient,
                quantity=quantity
            ))

        return self.chain[-1]['index'] + 1

    def proof_of_work(self, proof: int):
        """
        Перевірка знайденого доказу роботи алгоритмом PoW
        :param proof: доказ роботи користувача, який необхідно перевірити
        :return: підтверджений блок, якщо доказ роботи знайдено вірно, інакше None
        """
        template = {
            'index': len(self.chain) + 1,
            'time': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'prev_hash': self.chain[-1]['hash']
        }
        block = Block(**template)
        if block.validate_proof():
            return block
        return None
