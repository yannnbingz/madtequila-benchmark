import json
import orquestra.sdk.v2.dsl as sdk
#from typing import Union, Dict


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:kottmanj/qe-madtequila.git",
    git_ref="master",
)

TEQUILA_IMPORT = sdk.GitImport(repo_url="git@github.com:tequilahub/tequila.git", git_ref="master")
PYSCF_IMPORT = sdk.GitImport(repo_url="git@github.com:pyscf/pyscf.git", git_ref="master")
@sdk.task(
    source_import=THIS_IMPORT, 
    dependency_imports=[TEQUILA_IMPORT],
    custom_image="jgonthier/madtequila:latest",
)
def run_madness(geometry, n_pno, **kwargs):
    import qemadtequila as madtq
    SCHEMA_VERSION=madtq.SCHEMA_VERSION

    molgeometry=None
    geometry_str = ""
    if "sites" in geometry:
        molgeometry = geometry
    elif ".json" in geometry:
        with open(geometry) as f:
            molgeometry = json.load(f)
    else:
        geometry_str = geometry
    
    if molgeometry is not None:
        for atom in molgeometry["sites"]:
            geometry_str += "{} {} {} {}\n".format(
                atom["species"], atom["x"], atom["y"], atom["z"]
            )

    mol = madtq.run_madness(geometry=geometry_str, n_pno=n_pno)
    results_dict = {}
    results_dict["schema"] = SCHEMA_VERSION + "-madresults"
    results_dict["kwargs"] = kwargs
    results_dict["geometry"] = geometry
    results_dict["n_pno"] = n_pno
    json_string = madtq.mol_to_json(mol)
    results_dict["mol"]=json_string
    with open("madmolecule.json", "w") as f:
        f.write(json.dumps(results_dict, indent=2))


@sdk.task(
    source_import=THIS_IMPORT, 
    dependency_imports=[PYSCF_IMPORT],
    custom_image="jgonthier/madtequila:latest",
    n_outputs=1
)
def compute_pyscf_energy(madmolecule, method="fci", **kwargs):
    import qemadtequila as madtq
    mol = madtq.mol_from_json(madmolecule)
    energy = madtq.compute_pyscf_energy(mol, method=method, **kwargs)
    result = {"SCHEMA":"schema",
            "info":"{} - {}/MRA-PNO({},{})".format(mol.parameters.name, method, mol.n_electrons, 2*mol.n_orbitals),
            "energy":energy}
    with open("energy.json", "w") as f:
        f.write(json.dumps(result, indent=2))
    return energy


@sdk.workflow
def benchmarking_h2():
    """Workflow that generates random samples and fits them using a linear
    regression."""

    geometry = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "H","x": 0,"y": 0,"z": 0},
                            {"species": "H","x": 0,"y": 0,"z": 0.7}
                         ]
                }
    n_pno = 4
    run_madness(geometry, n_pno)
    energy = compute_pyscf_energy('madmolecule.json', method="fci")
    return energy

if __name__ == "__main__":
    benchmarking_h2()