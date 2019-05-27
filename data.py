import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Text, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from  sqlalchemy.sql.expression import func, select

engine = create_engine('sqlite:///sputaproblemi.db')
Session = sessionmaker(engine)
Base = declarative_base(engine)

def get_random_problem(country=None, gara=None):
    session = Session()
    if country == None:
        return session.query(Problema).order_by(func.random()).first()
    if gara == None:
        return session.query(Problema).join(Gara).filter(Gara.nazione==country).order_by(func.random()).first()
    return session.query(Problema).join(Gara).filter(Gara.nazione==country, Gara.nome==gara).order_by(func.random()).first()

class Gara(Base):
    __tablename__ = 'gara'

    id = Column(Integer, primary_key=True)
    nome = Column(String(50))
    anno = Column(Integer)
    nazione = Column(String(20))
    aops_id = Column(Integer)

    def __repr__(self):
        return "<Gara({} {} {}, id={})>".format(self.nazione, self.nome, self.anno, self.aops_id)

class Problema(Base):
    __tablename__ = 'problema'

    id = Column(Integer, primary_key=True)
    testo = Column(Text)
    numero = Column(Integer)
    aops_id = Column(Integer)
    aops_link = Column(String(100))
    difficolta = Column(Integer)
    dato = Column(Date)

    gara_id = Column(Integer, ForeignKey("gara.id"))
    gara = relationship(Gara, backref="problemi")

    def get_titolo(self):
        return "{} {}, {}.".format(self.gara.nome, self.gara.anno, self.numero)

    def __repr__(self):
        return "<Problema({} {} n. {}, id={})>".format(self.gara.nome, self.gara.anno, self.numero, self.aops_id)

def create_db():
    session = Session()
    Base.metadata.create_all(engine)
    session.commit()
    print("Database creato")

if __name__=="__main__":
    create_db()
