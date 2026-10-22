import sqlite3
import pandas as pd
from src.config import PROCESSED_DIR, ANALYSIS_DB
from src.models.data_validation import validate_frame


def test_csv_sqlite_consistency():
    with sqlite3.connect(ANALYSIS_DB.resolve().as_uri() + "?mode=ro", uri=True) as db:
        for level in ("france", "regions", "drom"):
            name = f"mortinatalite_{level}"
            expected = validate_frame(pd.read_csv(PROCESSED_DIR / f"{name}.csv"), "mortinatalite")
            actual = pd.read_sql_query(f"SELECT * FROM {name}",db)
            pd.testing.assert_frame_equal(expected,actual,check_dtype=False)
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA foreign_key_check").fetchall() == []
        notes = db.execute("SELECT source_value,source_note,value FROM observations WHERE source_note IS NOT NULL ORDER BY source_value").fetchall()
        assert len(notes) == 3
        assert ('2,9**','**',2.9) in notes
        assert ('4163*','*',4163.0) in notes
