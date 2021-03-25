from chimera_visualizations import *
import argparse
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("sqlid")
    parser.add_argument("pdbpath")
    parser.add_argument("chimerapath")
    args = parser.parse_args()
    sql_id = args.sqlid
    pdb_path = args.pdbpath
    chimera_path = args.chimerapath
    pdb_path = Path(pdb_path)
    chimera_path = Path(chimera_path)
    if not pdb_path.exists():
        raise Exception("Bad pdb dir path")
    if not chimera_path.exists():
        raise Exception("Bad chimera path")
    engine = create_engine("sqlite:///clique_traceback_v3.db", echo=True)
    meta = MetaData()
    cliques_table = Table(
        'cliques', meta,
        Column("id", Integer, primary_key=True),
        Column("size", Integer),
        Column("clique", String),
        Column("resid", String),
        Column("oldresid", String),
        Column("layerinfo", String),
        Column("pdbname", String)
    )
    meta.create_all(engine)

    conn = engine.connect()

    display_chimera(conn, sql_id, pdb_path, chimera_path)


if __name__ == "__main__":
    main()
