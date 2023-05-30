# © copyright by VoX DoX
import ssl
import certifi
from aiohttp import ClientSession
from typing import Optional, Union, Dict, List
from urllib.parse import urlencode
from hashlib import md5

from .models import (
	Currency,
	Balance,
	Invoice
)
from . import AsyncPayOkError, PayOkAPIError


class AsyncPayok:
	"""
	PayOk API class
	Асинхронный класс для работы с PayOk API
	Подробнее об API: https://payok.io/cabinet/documentation/doc_main.php
	:param api_key: ключ авторизации. Нужен для работы с API
	:type api_key: str
	:param secret_key: секретный ключ авторизации. Нужен для выставления счетов.
	:type secret_key: Optional[str]
	:param shop_id: ID кассы. Нужен для взаимодействия с определенной кассой
	:type shop_id: Optional[int]
	"""
	def __init__(
			self,
			api_id: int,
			api_key: str,
			secret_key: Optional[str],
			shop_id: Optional[int]
	) -> None:
		self.__API_URL__: str = "https://payok.io"
		self.__API_ID__: int = api_id
		self.__API_KEY__: str = api_key
		self.__SECRET_KEY__: Optional[str] = secret_key
		self.__SHOP_ID__: Optional[int] = shop_id

		self._SSL_CONTEXT_ = ssl.create_default_context(cafile=certifi.where())
		self.session: ClientSession = ClientSession()

	async def getBalance(
			self
	) -> Balance:
		"""
		Получение баланса аккаунта
		:return: баланс\Реф баланс
		:rtype: Balance
		"""
		params: dict = {
			"API_ID": self.__API_ID__,
			"API_KEY": self.__API_KEY__
		}
		method: str = "POST"
		url: str = self.__API_URL__ + "/api/balance"

		resp = await self._request(
			method=method,
			url=url,
			params=params
		)

		return Balance(**resp)

	async def getPayments(
			self,
			offset: Optional[int] = None
	) -> Union[Invoice, List[Invoice]]:
		"""
		Получение всех транзакций\транзакции
		:param offset: отсуп\пропуск указанного кол-ва строк
		:type offset: Optional[int]
		:return: данные об транзациях\транзакции
		:rtype: Union[Transaction, List[Transaction]
		"""
		method: str = "POST"
		url: str = self.__API_URL__ + "/api/transaction"
		data: dict = {
			"API_ID": self.__API_ID__,
			"API_KEY": self.__API_KEY__,
			"shop": self.__SHOP_ID__,
		}
		if offset:
			data["offset"] = offset

		response = await self._request(
			method=method,
			url=url,
			params=data
		)
		transactions = []
		for transaction in response.values():
			transactions.append(Invoice(**transaction))

		return transactions

	async def createInvoice(
			self,
			payment: Union[int, str],
			amount: float,
			currency: Optional[str] = Currency.RUB,
			desc: Optional[str] = 'Description',
			email: Optional[str] = None,
			success_url: Optional[str] = None,
			method: Optional[str] = None,
			lang: Optional[str] = None,
			custom: Optional[str] = None
	) -> str:
		"""
		Создание ссылки формы (инвойса) на оплату
		:param payment: уникальный айди платежа
		:type payment: Union[int, str]
		:param amount: сумма платежа
		:type amount: float
		:param currency: валюта платежа
		:type currency: Optional[str]
		:param desc: описание платежа
		:type desc: Optinal[str]
		:param email: почта плательщика
		:type email: Optional[str]
		:param success_url: ссылка для переадрессации после оплаты
		:type success_url: Optional[str]
		:param method: метод оплаты (см объект Method)
		:type method: Optional[str]
		:param lang:  язык интерфейса формы (RU - ENG)
		:type lang: Optional[str]
		:param custom: параметр для уведомления
		:type custom: Optional[str]
		:return: ссылку на форму оплаты
		:rtype: str
		"""
		if not self.__SECRET_KEY__:
			raise AsyncPayOkError("Invalid Secret Key - is empty!")

		params = {
			'amount': amount,
			'payment': payment,
			'shop': self.__SHOP_ID__,
			'currency': currency,
			'desc': desc,
			'email': email,
			'success_url': success_url,
			'method': method,
			'lang': lang,
			'custom': custom
		}

		for key, value in params.copy().items():
			if value is None:
				del params[key]

		sign_params = '|'.join(
			map(str, [
				amount, payment,
				self.__SHOP_ID__,
				currency, desc,
				self.__SECRET_KEY__
			]
				)).encode('utf-8')
		sign = md5(sign_params).hexdigest()
		params['sign'] = sign

		url = f'{self.__API_URL__}/pay?' + urlencode(params)
		return url

	async def _request(
			self,
			method: Optional[str],
			url: Optional[str],
			params: dict
	) -> Dict:
		"""
		Создание запроса к API
		:param method: метод запроса (POST, GET)
		:type method: Optional[str]
		:param url: ссылка запроса к API
		:type url: Optional[str]
		:param params: параметры запрсоа
		:type params: dict
		:return:
		"""
		request = await self.session.request(
			method=method,
			url=url,
			ssl_context=self._SSL_CONTEXT_,
			data=params,
		)
		if request.status == 401:
			raise AsyncPayOkError(
				"Invalid API KEY! You can get it here!"
			)
		answer: dict = await request.json(
			content_type="text/plain"
		)

		if answer.get("status") and answer.pop("status") == "error":
			desc = answer.get("text", answer.get("error_text"))
			code = answer["error_code"]
			raise PayOkAPIError(
				f"ERROR: {code} | {desc} \nCheck docs: https://payok.io/cabinet/documentation/doc_api_errors"
			)

		return answer
