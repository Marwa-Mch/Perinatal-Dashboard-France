import pandas as pd
import pytest
from src.views.naissance_views import calculer_variation, preparer_evolution_france, preparer_export_naissances
from src.views.analysis import creer_base_100
from src.views.mortinatalite_views import preparer_evolution_zone


def test_variation():
    assert calculer_variation(100,80) == -20
    assert calculer_variation(0,80) is None
    assert calculer_variation(float("nan"),80) is None


def test_empty_births():
    assert preparer_evolution_france(pd.DataFrame(), "naissances_totales").empty
    assert preparer_evolution_france(pd.DataFrame({"zone_géographique":["France"]}), "naissances_totales").empty


def test_birth_series_and_export():
    raw = pd.DataFrame({"2012_naissances_totales":[100],"2013_naissances_totales":[80]})
    result = preparer_evolution_france(raw,"naissances_totales")
    assert result["Nombre de naissances"].tolist() == [100,80]
    export = preparer_export_naissances(result)
    assert export.to_csv(index=False,sep=";").splitlines()[1] == "2012;100"
    assert list(raw.columns) == ["2012_naissances_totales","2013_naissances_totales"]


def test_base100():
    values = pd.DataFrame({"v":[200,100]})
    result = creer_base_100(values,"v")
    assert result["v — base 100"].tolist() == [100,50]
    assert creer_base_100(pd.DataFrame({"v":[0,10]}),"v")["v — base 100"].isna().all()


def test_effectif_2013_plural():
    frame = pd.DataFrame({"2013_mortinatalite_totale":[8],"2013_effectifs_naissances":[1000]})
    assert preparer_evolution_zone(frame)["Effectif des naissances"].iloc[0] == 1000
