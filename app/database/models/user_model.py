from datetime import datetime
from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    String, Integer, DateTime, BigInteger
)



class User(Base):
    __tablename__ = 'users'

    # INTEGER AUTO_INCREMENT PRIMARY KEY
    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True
    )
    # BIGINT, уникальный идентификатор Telegram
    tg_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True
    )
    # VARCHAR(128) для полного имени пользователя
    full_name: Mapped[str] = mapped_column(
        String(128), nullable=False
    )
    # VARCHAR(32) для username Telegram (может быть NULL)
    username: Mapped[str] = mapped_column(
        String(32), nullable=True
    )
    # DATETIME для времени регистрации
    registered_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False
    )
  