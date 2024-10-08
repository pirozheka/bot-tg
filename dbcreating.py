from sqlalchemy import create_engine
from sqlalchemy import  Column, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("sqlite:///bulletjournal.db", echo=True)
#При echo=True все операции с бд будут логгироваться на консоль

#создаем базовый класс для моделей
class Base(DeclarativeBase): pass

# создаем модель, объекты которой будут храниться в бд
class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    caption = Column(String, unique=True)
    category = Column(String, unique=True)
    body = Column(Text, nullable=False)

Base.metadata.create_all(bind=engine)


    

