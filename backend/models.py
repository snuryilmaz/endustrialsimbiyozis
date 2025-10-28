from sqlalchemy import Column, Integer, String, Float
from backend.db import Base

class Firma(Base):
    __tablename__ = "firmalar"
    id = Column(Integer, primary_key=True)
    ad = Column(String, nullable=False)
    sektor = Column(String, nullable=False)
    atik = Column(String)
    fiyat = Column(Float)
    miktar = Column(Float)
    lead_time_days = Column(Integer)
