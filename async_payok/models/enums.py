# © copyright by VoX DoX

class Currency:
    """
    Валюты, с которыми можно работать
    """
    RUB = 'RUB'
    UAH = 'UAH'
    USD = 'USD'
    EUR = 'EUR'


class Status:
    """
    Статус платежа
    """
    PAID: int = 1
    WAITING: int = 0


class WebHookStatus:
    """
    Статус вебхука
    """
    DELIVERED: int = 1
    NOT_DELIVERED: int = 0
    DELIVERED_ERROR: int = 2
