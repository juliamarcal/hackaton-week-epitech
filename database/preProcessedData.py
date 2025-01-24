from sqlalchemy import Column, String, Integer

# from  model import Base
# from database import Base
import database as db
# from base import Base

class PreProcessedData(db.Base):
    __tablename__ = 'pre-processed data'

    keyword = Column("keyword", String(64), primary_key=True)
    filePath = Column("filePath", String(128), primary_key=True)
    link = Column("fileLink", String(128))

    def __init__(self, keyword: str, filePath: str, link: str):
        """
        Adds a path to a pre-processed file.

        Arguments:
            keyword {str}: Keywords this file correspond to.
            filePath {str}: File path to the file.
            fileLink {str}: File link to download the file.
        """
        self.keyword = keyword
        self.filePath = filePath
        self.link = link