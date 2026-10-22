
"""
Reconstruction reproductible de la base SQLite
à partir des fichiers CSV préparés.
"""

import os
import re
import sqlite3
import tempfile

from contextlib import closing
from pathlib import Path

import pandas as pd

from src.config import ANALYSIS_DB, PROCESSED_DIR
from src.models.data_validation import validate_frame


def rebuild_database(
    destination=ANALYSIS_DB,
    processed=PROCESSED_DIR
):
    """
    Reconstruit la base SQLite à partir des CSV.

    La base est d'abord créée dans un fichier temporaire.
    Les contrôles d'intégrité sont effectués avant
    le remplacement de la base existante.

    La connexion SQLite est explicitement fermée
    avant le remplacement du fichier, notamment
    pour assurer la compatibilité avec Windows.
    """

    destination = Path(destination)
    processed = Path(processed)

    frames = {}
    raw_frames = {}

    # =================================================
    # 1. CHARGEMENT ET VALIDATION DES DONNÉES
    # =================================================

    for level in ("france", "regions", "drom"):

        name = f"mortinatalite_{level}"

        raw_frames[name] = pd.read_csv(
            processed / f"{name}.csv"
        )

        frames[name] = validate_frame(
            raw_frames[name],
            "mortinatalite"
        )

    # =================================================
    # 2. CRÉATION DU FICHIER TEMPORAIRE
    # =================================================

    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    fd, temporary = tempfile.mkstemp(
        suffix=".db",
        dir=destination.parent
    )

    os.close(fd)

    try:

        # =============================================
        # 3. OUVERTURE ET FERMETURE SÉCURISÉES
        # =============================================

        with closing(sqlite3.connect(temporary)) as db:

            # Gestion automatique de la transaction
            with db:

                db.execute(
                    "PRAGMA foreign_keys = ON"
                )

                # =====================================
                # 4. IMPORTATION DES TABLES CSV
                # =====================================

                for name, frame in frames.items():

                    frame.to_sql(
                        name,
                        db,
                        index=False,
                        if_exists="fail"
                    )

                # =====================================
                # 5. CRÉATION DU SCHÉMA RELATIONNEL
                # =====================================

                db.executescript(
                    """
                    CREATE TABLE territories (
                        id INTEGER PRIMARY KEY,
                        level TEXT NOT NULL,
                        name TEXT NOT NULL,
                        UNIQUE(level, name)
                    );

                    CREATE TABLE indicators (
                        code TEXT PRIMARY KEY,
                        unit TEXT NOT NULL
                    );

                    CREATE TABLE observations (
                        territory_id INTEGER NOT NULL
                            REFERENCES territories(id),

                        year INTEGER NOT NULL
                            CHECK(year BETWEEN 2012 AND 2023),

                        indicator_code TEXT NOT NULL
                            REFERENCES indicators(code),

                        value REAL CHECK(value >= 0),

                        source_value TEXT,
                        source_note TEXT,

                        PRIMARY KEY(
                            territory_id,
                            year,
                            indicator_code
                        )
                    );

                    CREATE INDEX observations_lookup
                    ON observations(
                        year,
                        indicator_code
                    );
                    """
                )

                # =====================================
                # 6. INSERTION DES INDICATEURS
                # =====================================

                for code in (
                    "mortinatalite_totale",
                    "mortinatalite_spontanee",
                    "img",
                    "effectif_naissances"
                ):

                    unit = (
                        "effectif"
                        if code == "effectif_naissances"
                        else "pour_mille"
                    )

                    db.execute(
                        """
                        INSERT INTO indicators
                        VALUES (?, ?)
                        """,
                        (code, unit)
                    )

                # =====================================
                # 7. INSERTION DES OBSERVATIONS
                # =====================================

                for name, frame in frames.items():

                    for row_index, row in frame.iterrows():

                        cursor = db.execute(
                            """
                            INSERT INTO territories(
                                level,
                                name
                            )
                            VALUES (?, ?)
                            """,
                            (
                                name.removeprefix(
                                    "mortinatalite_"
                                ),
                                row["zone_geographique"]
                            )
                        )

                        territory_id = cursor.lastrowid

                        for column in frame:

                            match = re.fullmatch(
                                r"(20\d{2})_(.+)",
                                column
                            )

                            if not match:
                                continue

                            year, code = match.groups()

                            code = code.replace(
                                "effectifs_naissances",
                                "effectif_naissances"
                            )

                            value = row[column]

                            raw = raw_frames[name].loc[
                                row_index,
                                column
                            ]

                            raw_text = (
                                None
                                if pd.isna(raw)
                                else str(raw)
                            )

                            marker = re.search(
                                r"(\*+)$",
                                raw_text or ""
                            )

                            db.execute(
                                """
                                INSERT INTO observations
                                VALUES (?, ?, ?, ?, ?, ?)
                                """,
                                (
                                    territory_id,
                                    int(year),
                                    code,
                                    (
                                        None
                                        if pd.isna(value)
                                        else float(value)
                                    ),
                                    raw_text,
                                    (
                                        marker.group(1)
                                        if marker
                                        else None
                                    )
                                )
                            )

                # =====================================
                # 8. CONTRÔLES D'INTÉGRITÉ
                # =====================================

                foreign_key_errors = db.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()

                if foreign_key_errors:
                    raise ValueError(
                        "Intégrité référentielle incorrecte."
                    )

                integrity_result = db.execute(
                    "PRAGMA integrity_check"
                ).fetchone()

                if integrity_result[0] != "ok":
                    raise ValueError(
                        "Intégrité SQLite incorrecte."
                    )

        # =============================================
        # 9. REMPLACEMENT DE LA BASE
        # =============================================

        # La connexion est fermée à ce stade.
        os.replace(
            temporary,
            destination
        )

    finally:

        # Nettoyage du fichier temporaire
        # s'il existe encore.
        Path(temporary).unlink(
            missing_ok=True
        )
