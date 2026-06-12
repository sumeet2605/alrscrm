import os
import subprocess
import sys
from pathlib import Path


def test_sales_seed_registers_related_models_before_mapper_configuration():
    env = os.environ.copy()
    env["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
    script = (
        "from sqlalchemy.orm import configure_mappers; "
        "import app.sales.seeds; "
        "configure_mappers()"
    )
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            script,
        ],
        check=False,
        env=env,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, result.stderr
