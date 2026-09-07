from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..db import Base


class NumberingSequence(Base):
    """key=前缀或业务键；date=YYYYMMDD（静态编号为 'static'）；last_no=当日/全局已发最大流水"""

    __tablename__ = "numbering_sequences"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    date: Mapped[str] = mapped_column(String(10), primary_key=True)
    last_no: Mapped[int] = mapped_column(Integer, default=0)
