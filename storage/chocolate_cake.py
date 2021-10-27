from sqlalchemy import Column, Integer, String, DateTime
from base import Base
import datetime


class ChocolateCake(Base):
    """Chocolate Cake"""

    __tablename__ = "chocolate_cake"

    cake_id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    chocolate_type = Column(String(250), nullable=False)
    preparation_method = Column(String(250), nullable=False)
    sell_by_date = Column(String(100), nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, cake_id, name, chocolate_type, preparation_method, sell_by_date):
        """Initializes a Chocolate Cake Order"""
        self.cake_id = cake_id
        self.name = name
        self.chocolate_type = chocolate_type
        self.preparation_method = preparation_method
        self.sell_by_date = sell_by_date
        self.date_created = datetime.datetime.now() # Sets the date/time record is created


    def to_dict(self):
        """Dictionary Representation of a Chocolate Cake Order"""
        dict = {}
        dict['cake_id'] = self.cake_id 
        dict['name'] = self.name
        dict['chocolate_type'] = self.chocolate_type
        dict['preparation_method'] = self.preparation_method
        dict['sell_by_date'] = self.sell_by_date
        dict['date_created'] = self.date_created

        return dict
