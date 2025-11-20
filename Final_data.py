from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import wraps

engine = create_engine('sqlite:///pokedex.db', echo=False)

Base = declarative_base()

# Name, id, forms/megas, description, height, weight, types, generos, weaknesses, stats, evolutions, image
class Pokemon(Base):
    __tablename__ = 'pokemons'
    name = Column(String, nullable=False)
    id = Column(String, primary_key=True)
    description_x = Column(Text, nullable=True)
    description_y = Column(Text, nullable=True)
    height = Column(Text, nullable=False)
    weight = Column(Text, nullable=False)
    types = Column(JSON, nullable=False) 
    image = Column(String, nullable=True)
    gender = Column(String, nullable=True)
    stats = Column(JSON, nullable=False)
    abilities = Column(JSON, nullable=False)
    weaknesses_4X = Column(JSON, nullable=False)
    weaknesses_2X = Column(JSON, nullable=False)
    evolution_chain = Column(JSON, nullable=False)

# Criar todas as tabelas no banco de dados
Base.metadata.create_all(engine)


# Criar uma sessão para interagir com o banco de dados
Session = sessionmaker(bind=engine)
session = Session()


