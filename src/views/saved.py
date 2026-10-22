"""Création, lecture, renommage et suppression d’analyses personnelles."""
import streamlit as st
from src.controllers import saved_controller as controller
from src.controllers.analysis_controller import get_requete_classement_regions
from src.models.session import get_current_user, protected_download_button

LABELS = {"Mortinatalité totale": "mortinatalite_totale",
          "Mortinatalité spontanée": "mortinatalite_spontanee", "IMG": "img"}


def load_view():
    st.title("Mes analyses enregistrées")
    st.write("Conservez les paramètres d’un classement régional pour le retrouver lors d’une prochaine visite.")
    if not get_current_user():
        st.info("Connectez-vous pour enregistrer et retrouver vos analyses.")
        return
    st.caption("Chaque compte accède uniquement à ses propres analyses. Les résultats sont recalculés à partir des données disponibles.")
    with st.form("save_analysis"):
        name = st.text_input("Nom de l’analyse", max_chars=80)
        year = st.selectbox("Année", list(range(2012, 2024)), index=11)
        label = st.selectbox("Indicateur", list(LABELS))
        limit = st.number_input("Nombre de régions", min_value=1, max_value=13, value=10, step=1)
        if st.form_submit_button("Enregistrer"):
            controller.create_saved(name, year, LABELS[label], limit)
            st.success("Analyse enregistrée.")
    rows = controller.list_saved()
    if not rows:
        st.info("Aucune analyse enregistrée pour le moment.")
        return
    by_id = {row["id"]: row for row in rows}
    identifier = st.selectbox("Retrouver une analyse", list(by_id), format_func=lambda value: by_id[value]["name"])
    row = by_id[identifier]
    params = row["parameters"]
    st.caption(f"Année : {params['year']} · Indicateur : {params['indicator']} · Nombre de régions : {params['limit']}")
    _, result = get_requete_classement_regions(params["year"], params["indicator"], params["limit"])
    st.dataframe(result, hide_index=True, width="stretch")
    protected_download_button("Télécharger ce classement", data=result.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"), file_name="classement_enregistre.csv", mime="text/csv")
    with st.form("rename_analysis"):
        new_name = st.text_input("Nouveau nom", value=row["name"], max_chars=80)
        if st.form_submit_button("Renommer"):
            controller.rename_saved(identifier, new_name)
            st.rerun()
    confirmed = st.checkbox("Je confirme la suppression de cette analyse")
    if st.button("Supprimer l’analyse", disabled=not confirmed):
        controller.delete_saved(identifier)
        st.rerun()
