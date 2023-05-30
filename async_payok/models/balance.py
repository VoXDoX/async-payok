# © copyright by VoX DoX
from pydantic import BaseModel


class Balance(BaseModel):
	"""
	Balance model PayOk
	"""
	balance: float
	ref_balance: float
