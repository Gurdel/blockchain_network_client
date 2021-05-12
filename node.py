from urllib.parse import urlparse


class Node(dict):
    """
    Клас для збереження адрес інших користувачів
    """
    def __init__(self, link: str):
        """
        Парсить отриману адресу та зберігає в класі
        Наприклад http://127.0.0.1:5000
        :param link: адреса користувача
        """
        parsed_url = urlparse(link)
        if parsed_url.netloc:
            dict.__init__(self, link=parsed_url.netloc)
        elif parsed_url.path:
            dict.__init__(self, link=parsed_url.path)
        else:
            raise ValueError('Invalid URL')
