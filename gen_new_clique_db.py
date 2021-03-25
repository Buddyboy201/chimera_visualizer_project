from TPP.API.top_pro_pack import Project, create_project
from pathlib import Path
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
import time


pdb_directory = Path(r"C:\test_proteins\Menv_color\Menv_color")
out_dir = Path(r"C:\test_proteins\Menv_log_out\Menv_log_out")

pdb_file_names = [f.name for f in pdb_directory.iterdir() if f.suffix == ".pdb"]
out_file_names = [f.name for f in out_dir.iterdir() if f.suffix == ".out" and "id" not in f.name]
pdb_file_names.sort()
out_file_names.sort()
# pdb_file_names.pop(390)

config_path = Path.cwd() / Path("dbv3_config.json")

create_project(config_path, "dbv3", pdb_directory, Path.cwd() / Path("../temp_json_dir"), ignored_paths=[pdb_directory / Path(pdb_file_names[390])], exclude_backbone=True)
proj = Project(config_path)
proj.add_ignored_path(Path(r"C:\test_proteins\Menv_color\Menv_color\list"))
proj.load_all_pdbs([f.stem if f not in proj.list_ignored() else "" for f in proj.list_pdb_files()])

# TODO: Fix bug pertaining to assigning ids to ignored files, currently having to explicitly include ignored file's id to run proj.load_all_proteins(ids)


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

def get_filtered_out_lines(out_file):
    with open(out_file, "rt") as file:
        lines = file.readlines()
        return [[i for i in line.split(" ") if i != ""] for line in lines if line.split(" ")[0].strip(" ") == "2016Menv"]


def get_layer_resid(resid, layer_ref):
    return layer_ref[resid + 1]

def get_clique_with_names_only(clique):
    clique.sort(key=lambda x: x.name)
    return ";".join([i.name for i in clique])

def get_clique_with_resid_only(clique):
    clique.sort(key=lambda x: x.name)
    return ";".join([str(i.resid) for i in clique])

def get_clique_with_old_resid_only(clique):
    clique.sort(key=lambda x: x.name)
    return ";".join([str(i.old_resid) for i in clique])

def get_clique_layer_info_only(clique, layer_ref):
    clique.sort(key=lambda x: x.name)
    resids = [res.resid for res in clique]
    return ";".join([str(get_layer_resid(resid, layer_ref)) for resid in resids])

def push_clique_to_buffer(clique, pdb_name, layer_ref, buffer):
    buffer.append({"size": len(clique), "clique": get_clique_with_names_only(clique), "resid": get_clique_with_resid_only(clique), "oldresid": get_clique_with_old_resid_only(clique),
                   "layerinfo": get_clique_layer_info_only(clique, layer_ref), "pdbname": pdb_name})

def bulk_insert_cliques_into_db(buffer, conn, table):
    return conn.execute(table.insert(), buffer)


def insert_clique_into_db(clique, pdb_name, layer_ref, conn, table):
    ins = table.insert().values(size=len(clique), clique=get_clique_with_names_only(clique),
                                resid=get_clique_with_resid_only(clique), oldresid=get_clique_with_old_resid_only(clique), layerinfo=get_clique_layer_info_only(clique, layer_ref), pdbname=pdb_name)
    result = conn.execute(ins)
    return result

min_hydrophobic_residues = 14 # TODO: need to increase (maybe 16?)

for pdb_id in proj.proteins:
    if Path(out_dir / Path("{}.out".format(pdb_id))).is_file():
        print("out file found for {}".format(pdb_id))
        hydrophobic_count = 0
        layer_ref = {}
        content = get_filtered_out_lines(Path(out_dir / Path("{}.out".format(pdb_id))))
        for line in content:
            res = line[2].strip(" ")
            id = int(line[1].strip(" "))
            layer = int(line[4].strip(" "))
            layer_ref[id] = layer
            if layer == 3 or layer == 4:
                hydrophobic_count += 1
        if hydrophobic_count >= min_hydrophobic_residues:
            P = proj.get_protein(pdb_id)
            assert len(layer_ref) == len(P.residues)
            cliques = P.centroid_cliques
            buffer = []
            for clique in cliques:
                # insert_clique_into_db(clique, P.name, layer_ref, conn, cliques_table)
                push_clique_to_buffer(clique, P.name, layer_ref, buffer)
            bulk_insert_cliques_into_db(buffer, conn, cliques_table)
        else:
            print("id {} for P.name with out file {} does not meet hydrophobicity requirements".format(pdb_id, Path(out_dir / Path("{}.out".format(pdb_id)))))

    else:
        print("out file for {} does not exist in {}".format(pdb_id, out_dir))



































# check out python pretty table and fastapi/typer modules













# DONE - TODO: (12/20/20) finish implementing Project methods ['ignore_protein', 'load_all_pdb', 'load_all_json', 'remove_protein']
# DONE - TODO: (12/20/20) finish adding name-file_path linking system for protein data (pdb/json) in config files for project
# DONE - TODO: (12/20/20) push Project class changes to github repo as soon as possible
# DONE - TODO: (12/20/20) create project for rsch proteins and update database with mainchain atoms excluded
# DONE - TODO: (12/20/20) analyze average sequence distance distribution for cliques in new database
# DONE - TODO: (12/20/20) randomly sample 50 cliques and take notes on validity for quality control
# DONE - TODO: (12/20/20) SEND UPDATE TO VLADIMIR AND CO AFTER THE ABOVE STEPS ARE COMPLETED STAT
# DONE - TODO: (1/2/21) finish energyND class code
# DONE - TODO: (1/3/21) debug energyND class code
# TODO: (IDK lol) finish energyND visualization