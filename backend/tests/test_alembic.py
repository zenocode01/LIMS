import os
import subprocess
import sys


def test_alembic_upgrade_head(tmp_path):
    db_file = tmp_path / "alembic_test.db"
    env = {**os.environ, "DATABASE_URL": f"sqlite:///{db_file}"}
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=".", env=env, capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stderr
    assert db_file.exists()
