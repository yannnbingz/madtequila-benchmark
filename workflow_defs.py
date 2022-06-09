import json
import geometries
import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/madtequila-benchmark.git",
    git_ref="main",
)

MADTEQUILA_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/yz-openshell-madtequila.git", 
    git_ref="main",
)

# MADTEQUILA_IMPORT = sdk.GitImport(
#     repo_url="git@github.com:yannnbingz/yz-openshell-madtequila.git", 
#     git_ref="li-openshell",
# )

@sdk.task(
    source_import=THIS_IMPORT, 
    dependency_imports=[MADTEQUILA_IMPORT],
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

    print("*** MOLECULE GEOMETRY OBTAINED ***")
    mol = madtq.run_madness(geometry=geometry_str, n_pno=n_pno, **kwargs)
    print("*** MOL OBJECT DEFINED, INTEGRALS GENERATED ***")

    results_dict = {}
    results_dict["schema"] = SCHEMA_VERSION + "-madresults"
    results_dict["kwargs"] = kwargs
    results_dict["geometry"] = geometry
    results_dict["n_pno"] = n_pno
    json_string = madtq.mol_to_json(mol)
    results_dict["mol"]=json_string

    return mol, results_dict
    

@sdk.task(
    source_import=THIS_IMPORT, 
    dependency_imports=[MADTEQUILA_IMPORT],
    custom_image="jgonthier/madtequila:latest",
    n_outputs=1
)
def compute_pyscf_energy(mol, method="fci", **kwargs):
    import qemadtequila as madtq

    print("***CALLING PYSCF***")
    energy = madtq.compute_pyscf_energy(mol, method=method, **kwargs)
    result = {"SCHEMA":"schema",
            "info":"{} - {}/MRA-PNO({},{})".format(mol.parameters.name, method, mol.n_electrons, 2*mol.n_orbitals),
            "energy":energy}
    print("***PYSCF RESULT: ***\n", result)

    return energy

@sdk.workflow
def benchmarking_project():
    """Workflow that generates random samples and fits them using a linear
    regression."""

    geometry = geometries.geometry_def('h2')
    n_pno = 2
    pyscf_method = 'ccsd(t)'
    mol, madmolecule = run_madness(geometry, n_pno)
    energy = compute_pyscf_energy(mol, method=pyscf_method)
    return (energy, madmolecule)

if __name__ == "__main__":
    benchmarking_project()


#TEQUILA_IMPORT = sdk.GitImport(repo_url="git@github.com:tequilahub/tequila.git", git_ref="master")
#PYSCF_IMPORT = sdk.GitImport(repo_url="git@github.com:pyscf/pyscf.git", git_ref="master")

    #dependency_imports=[MADTEQUILA_IMPORT, TEQUILA_IMPORT],
    #dependency_imports=[MADTEQUILA_IMPORT, TEQUILA_IMPORT, PYSCF_IMPORT],

    # with open("madmolecule.json", "w") as f:
    #    f.write(json.dumps(results_dict, indent=2))
    # print("***INTEGRAL RESULT WRITTEN TO: madmolecule.json ***")

    # with open("energy.json", "w") as f:
    #     f.write(json.dumps(result, indent=2))
    # print("***ENERGY RESULT WRITTEN TO: energy.json ***")