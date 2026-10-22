import sqlite3
import pandas as pd
import pytest
from src.models import analysis_model
from src.models.build_data import rebuild_database
from src.models.data_validation import validate_frame
from src.controllers.analysis_controller import get_requete_classement_regions, get_statistiques_regions

@pytest.fixture
def analysis_db(tmp_path, monkeypatch):
    processed = tmp_path / "processed"
    processed.mkdir()
    for level in ("france", "regions", "drom"):
        pd.DataFrame({"zone_geographique": ["A", "B", "C"],
            "2023_mortinatalite_totale": [5.0, 10.0, None],
            "2023_mortinatalite_spontanee": [3.0, 6.0, None],
            "2023_img": [2.0, 4.0, None],
            "2023_effectif_naissances": [100, 200, 300]}).to_csv(processed / f"mortinatalite_{level}.csv", index=False)
    path = tmp_path / "analysis.db"
    rebuild_database(path, processed)
    monkeypatch.setattr(analysis_model, "DATABASE_PATH", path)
    analysis_model.executer_requete_sql.clear()
    analysis_model.lire_table_sqlite.clear()
    yield path
    analysis_model.executer_requete_sql.clear()
    analysis_model.lire_table_sqlite.clear()


def test_ranking_and_stats(analysis_db):
    _, ranking = get_requete_classement_regions(2023, "mortinatalite_totale", 1)
    assert ranking.to_dict("records") == [{"region": "B", "valeur": 10.0}]
    _, stats = get_statistiques_regions(2023, "mortinatalite_totale")
    assert stats.iloc[0].to_dict() == {"nombre_regions": 2, "moyenne": 7.5, "minimum": 5.0, "maximum": 10.0}


@pytest.mark.parametrize("year,indicator,limit", [(2011,"img",10),(2024,"img",10),('2023',"img",10),
    (True,"img",10),(2023,"other",10),(2023,"img",0),(2023,"img",101),(2023,"img",1.5),
    (2023,"img",True),(2023,"img; DROP TABLE users",10)])
def test_invalid_selection(year, indicator, limit):
    with pytest.raises(ValueError):
        get_requete_classement_regions(year, indicator, limit)


def test_stats_year_checked():
    with pytest.raises(ValueError):
        get_statistiques_regions("2023", "img")


def test_readonly_connection(analysis_db):
    with pytest.raises(ValueError):
        analysis_model.executer_requete_sql("DELETE FROM observations")
    with pytest.raises(Exception):
        analysis_model.executer_requete_sql("SELECT 1; DROP TABLE observations")
    with sqlite3.connect(analysis_db) as db:
        assert db.execute("SELECT COUNT(*) FROM observations").fetchone()[0] == 36
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("INSERT INTO observations(territory_id, year, indicator_code, value) VALUES(1,2023,'img',5)")


def test_data_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(analysis_model, "DATABASE_PATH", tmp_path / "absent.db")
    analysis_model.lire_table_sqlite.clear()
    with pytest.raises(FileNotFoundError):
        analysis_model.lire_table_sqlite("mortinatalite_france")
    assert not (tmp_path / "absent.db").exists()


@pytest.mark.parametrize("data", [{}, {"x":[1]}, {"zone_geographique":[None],"2023_img":[1]},
    {"zone_geographique":["A","A"],"2023_img":[1,2]},
    {"zone_geographique":["A"],"2023_img":[-1]},
    {"zone_geographique":["A"],"2023_img":["erreur"]}])
def test_data_rejected(data):
    with pytest.raises(ValueError):
        validate_frame(pd.DataFrame(data), "mortinatalite")


def test_annotated_numbers():
    raw = pd.DataFrame({"zone_geographique":["A"],"2023_img":["2,9**"], "2023_effectif_naissances":["4163*"]})
    clean = validate_frame(raw, "mortinatalite")
    assert clean["2023_img"].iloc[0] == 2.9
    assert clean["2023_effectif_naissances"].iloc[0] == 4163
    assert raw["2023_img"].iloc[0] == "2,9**"
