from datetime import date, timedelta

import pytest

from app.numbering import service as ns


def test_quote_format(db_session):
    assert ns.no_quote(db_session) == f"Q-{date.today():%Y%m%d}-001"


def test_daily_sequence_increments(db_session):
    a = ns.no_entrustment(db_session)
    b = ns.no_entrustment(db_session)
    assert a.endswith("-001") and b.endswith("-002")


def test_daily_reset(db_session):
    d1 = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    ns.take_number(db_session, "C", day=d1)
    ns.take_number(db_session, "C", day=d1)
    n = ns.take_number(db_session, "C")  # 今天
    assert n == 1


def test_sample_biz_segment(db_session):
    assert ns.no_sample(db_session).startswith("S-EMC-")
    assert ns.no_sample(db_session, biz="SAF").startswith("S-SAF-")


def test_record_format(db_session):
    r = ns.no_record(db_session, "TR", 4, 4)
    assert r.startswith("TR4-004-") and r.endswith("-001")
    r2 = ns.no_record(db_session, "QR", 1, 1)
    assert r2.startswith("QR1-001-")


def test_record_bad_prefix(db_session):
    with pytest.raises(AssertionError):
        ns.no_record(db_session, "XX", 1, 1)


def test_report_batch_per_entrustment(db_session):
    a = ns.no_report(db_session, "C-20260904-001")
    b = ns.no_report(db_session, "C-20260904-001")
    c = ns.no_report(db_session, "C-20260904-002")
    assert a == "R-C-20260904-001-01"
    assert b == "R-C-20260904-001-02"
    assert c == "R-C-20260904-002-01"


def test_static_sequence(db_session):
    assert ns.no_equipment(db_session) == "EQ-001"
    assert ns.no_customer(db_session) == "CU-001"
    assert ns.no_equipment(db_session) == "EQ-002"
