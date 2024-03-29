# © copyright by VoX DoX
from typing import Union, Optional
from pydantic import BaseModel, Field


class Invoice(BaseModel):
	"""
	Invoice model Payok
	"""
	transaction: int
	email: str
	amount: float
	currency: str
	currency_amount: float
	comission_percent: float
	comission_fixed: float
	amount_profit: float
	method: str
	payment_id: Union[int, str]
	description: str
	date: str
	pay_date: str
	transaction_status: int
	custom_fields: Optional[str]
	webhook_status: int
	webhook_amount: int
