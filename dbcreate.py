# Импорт необходимых классов и функций из библиотеки SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import DeclarativeBase

# Создаем движок для подключения к базе данных SQLite
engine = create_engine("sqlite:///bulletjournal.db", echo=True)  
# При echo=True все операции с БД будут логгироваться на консоль

# Создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass

# Определяем модель для заметок
class Note(Base):
    __tablename__ = 'notes'  # Название таблицы в базе данных

    # Определение столбцов таблицы
    id = Column(Integer, primary_key=True, index=True)  # Уникальный идентификатор заметки
    caption = Column(String, unique=True)  # Заголовок заметки, должен быть уникальным
    category = Column(String, nullable=False)  # Категория заметки, обязательное поле
    body = Column(Text, nullable=False)  # Текст заметки, обязательное поле
    timer = Column(DateTime, nullable=True)  # Таймер для напоминания, может быть пустым
    chat_id = Column(Integer, nullable=False)  # ID чата, обязательное поле

# Создаем все таблицы в базе данных
Base.metadata.create_all(bind=engine)
