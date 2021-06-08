from hashlib import sha256
import json


class Transaction(dict):
    """
    Клас для збереження транзакцій у мережі
    """
    def __init__(self, sender: str, recipient: str, quantity: float, message: str = '', signature: str = '',
                 key: tuple = (0, 0)):
        """
        Конструктор класу
        :param sender: відправник
        :param recipient: отримувач
        :param quantity: кількість умовних одиниць
        """
        dict.__init__(self, sender=sender, recipient=recipient, quantity=quantity, message=message,
                      signature=signature, key=key)

    def get_transaction_hash(self) -> str:
        """
        Обраховує та повертає хеш транзакції, використовуючи хеш-функцію sha256
        :return: хеш даної транзакції
        """
        transaction_string = json.dumps(self, sort_keys=True).encode()
        return sha256(transaction_string).hexdigest()
