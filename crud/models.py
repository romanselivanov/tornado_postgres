from sqlalchemy import Column, BigInteger, String, JSON, Integer
from crud.database import Base


class RequestBody(Base):
    __tablename__ = 'request_body'

    id = Column(BigInteger, primary_key=True)
    body = Column(JSON)
    key = Column(String)
    request_count = Column(Integer)
