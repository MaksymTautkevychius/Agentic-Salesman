from typing import TypedDict

class PersonalData:
    def __init__(self, name: str, phone_number: str, address: str):
        self._name = name
        self._phone_number = phone_number
        self._address = address

class Order:
    def __init__(self, product_name : str, id: int):
        self._product_name = product_name
        self._id = id

class Lead:
    def __init__(self,id,order,personal_data):
        self.id = id
        self._Order = order
        self._personal_data = personal_data