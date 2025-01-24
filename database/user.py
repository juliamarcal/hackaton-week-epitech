from sqlalchemy import Column, String
from sqlalchemy_utils import EmailType

# from  model import Base
# from database import Base
import database as db
# from base import Base

class User(db.Base):
    __tablename__ = 'user'

    email = Column("userEmail", EmailType, primary_key=True)
    password = Column("userPassword", String(50), nullable=False)

    def __init__(self, email: str, password: str):
        """
        Creates an user.

        Arguments:
            email {str}: Email.
            password {str}: Password.
        """
        self.email = email
        self.password = password    