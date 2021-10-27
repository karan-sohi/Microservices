from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class VanillaCake(Base):
    """Vanilla Cake"""

    __tablename__ = "vanilla_cake"

    cake_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    vanilla_type = Column(String(250), nullable=False)
    preparation_method = Column(String(250), nullable=False)
    sell_by_date = Column(String(250), nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, cake_id, name, vanilla_type, preparation_method, sell_by_date):
        """Initializes a Vanilla Cake Order"""
        self.cake_id = cake_id
        self.name = name
        self.vanilla_type = vanilla_type
        self.preparation_method = preparation_method
        self.sell_by_date = sell_by_date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """Dictionary Representation of a Vanilla Cake Order"""
        dict = {}
        dict['cake_id'] = self.cake_id 
        dict['name'] = self.name
        dict['vanilla_type'] = self.vanilla_type
        dict['preparation_method'] = self.preparation_method
        dict['sell_by_date'] = self.sell_by_date
        dict['date_created'] = self.date_created

        return dict
