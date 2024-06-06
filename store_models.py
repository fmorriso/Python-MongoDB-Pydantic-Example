from typing import ClassVar

from pyodmongo import DbModel


class Product(DbModel):
    """Database: store, collection: products"""
    name: str
    price: int
    category: str
    image: str
    id_visible: int
    _collection: ClassVar = 'products'
