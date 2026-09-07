"""编号服务 — 编号规则 v2（见设计规格 §7）。

统一骨架: 前缀[-业务线][-层级][模板号]-YYYYMMDD-流水，流水 3 位按日归零。
"""
from datetime import date

from sqlalchemy.orm import Session

from ..models.sequence import NumberingSequence

STATIC_DAY = "static"


def take_number(db: Session, key: str, day: str | None = None) -> int:
    """key 在 day（默认今天；STATIC_DAY=全局）内的下一流水。

    PG 下用行锁防并发；SQLite 单进程天然串行。
    """
    d = day or date.today().strftime("%Y%m%d")
    row = (
        db.query(NumberingSequence)
        .filter_by(key=key, date=d)
        .with_for_update()
        .first()
    )
    if row is None:
        db.add(NumberingSequence(key=key, date=d, last_no=0))
        db.flush()
        row = (
            db.query(NumberingSequence)
            .filter_by(key=key, date=d)
            .with_for_update()
            .first()
        )
    row.last_no += 1
    db.flush()
    return row.last_no


def take_daily(db: Session, prefix: str) -> int:
    return take_number(db, prefix)


def take_static(db: Session, prefix: str) -> int:
    return take_number(db, prefix, day=STATIC_DAY)


def no_quote(db: Session) -> str:
    return f"Q-{date.today():%Y%m%d}-{take_daily(db, 'Q'):03d}"


def no_entrustment(db: Session) -> str:
    return f"C-{date.today():%Y%m%d}-{take_daily(db, 'C'):03d}"


def no_sample(db: Session, biz: str = "EMC") -> str:
    return f"S-{biz}-{date.today():%Y%m%d}-{take_daily(db, f'S-{biz}'):03d}"


def no_task(db: Session) -> str:
    return f"T-{date.today():%Y%m%d}-{take_daily(db, 'T'):03d}"


def no_record(db: Session, prefix: str, level: int, template_no: int) -> str:
    """技术/质量记录: TR4-004-20250623-001。level=表单层级 1-4。"""
    assert prefix in ("TR", "QR"), f"非法记录前缀 {prefix}"
    key = f"{prefix}{level}-{template_no:03d}"
    return f"{key}-{date.today():%Y%m%d}-{take_daily(db, key):03d}"


def no_report(db: Session, entrust_no: str) -> str:
    """报告: R-{委托单号}-{批次2位}，批次按委托单全局递增（不按日）。"""
    return f"R-{entrust_no}-{take_number(db, f'R-{entrust_no}', day=STATIC_DAY):02d}"


def no_equipment(db: Session) -> str:
    return f"EQ-{take_static(db, 'EQ'):03d}"


def no_customer(db: Session) -> str:
    return f"CU-{take_static(db, 'CU'):03d}"
