import json
import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/madtequila-benchmark.git",
    git_ref="main",
)

MADTEQUILA_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/yz-openshell-madtequila.git",
    git_ref="o2",
)

@sdk.task(
    source_import=THIS_IMPORT,
    dependency_imports=[MADTEQUILA_IMPORT],
    custom_image="yannnbingz/m1-madness-tequila:amd64",
    n_outputs=2,
    #resources=sdk.Resources(cpu='6000m', memory='6Gb')
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
    results_dict['schema'] = SCHEMA_VERSION + "-madresults"
    results_dict['kwargs'] = kwargs
    results_dict['geometry'] = geometry
    results_dict['n_pno'] = n_pno
    json_string = madtq.mol_to_json(mol)
    results_dict['mol']=json_string

    return mol, results_dict


@sdk.task(
    source_import=THIS_IMPORT,
    dependency_imports=[MADTEQUILA_IMPORT],
    custom_image="yannnbingz/m1-madness-tequila:amd64",
    n_outputs=1
)
def compute_pyscf_energy(mol, method="fci", **kwargs):
    import qemadtequila as madtq

    print("***CALLING PYSCF***")
    energy = madtq.compute_pyscf_energy(mol, method=method, **kwargs)
    results_dict = {}
    results_dict['SCHEMA'] = "schema"
    results_dict['name'] = mol.parameters.name
    results_dict['method'] = method
    results_dict['n_electrons'] = mol.n_electrons
    results_dict['n_orbitals'] = mol.n_orbitals
    results_dict['energy'] = energy
    mra_pno = "({},{})".format(mol.n_electrons, ", ", 2*mol.n_orbitals)
    print("*** MRA-PNO ***: \n")
    print(mra_pno)
    print("*** PYSCF ENERGY: ***\n")
    print(energy)

    return results_dict

@sdk.task(
        source_import=THIS_IMPORT,
)
def geometry_def(geo_name):

    H2 = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "H","x": 0,"y": 0,"z": 0},
                            {"species": "H","x": 0,"y": 0,"z": 0.7},
                        ]
        }
    H4 = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "H","x": 0,"y": 0,"z": 0},
                            {"species": "H","x": 0,"y": 0,"z": 0.75},
                            {"species": "H","x": 0.75,"y": 0,"z": 0.0},
                            {"species": "H","x": 0.75,"y": 0,"z": 0.75},
                        ]
        }
    Li = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "Li","x": 0,"y": 0,"z": 0},
                        ]
        }
    O2 = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "O","x": 0,"y": 0,"z": 0.602900000000},
                            {"species": "O","x": 0,"y": 0,"z": -0.602900000000},
                        ]
        }
    H2O = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "H","x": -0.000000000000,"y":  0.754700000000,"z": -0.521394777902},
                            {"species": "H","x":  0.000000000000,"y": -0.754700000000,"z": -0.521394777902},
                            {"species": "O","x": -0.000000000000,"y":  0.000000000000,"z":  0.065705222098},
                        ]
        }
    CH4 = {"schema": "molecular_geometry",
                "sites": [
                            {"species": "C","x": -0.000000000000,"y":  0.000000000000,"z": -0.000000000000},
                            {"species": "H","x":  0.886146218183,"y":  0.000000000000,"z":  0.626600000000},
                            {"species": "H","x": -0.886146218183,"y": -0.000000000000,"z":  0.626600000000},
                            {"species": "H","x": -0.000000000000,"y":  0.886146218183,"z": -0.626600000000},
                            {"species": "H","x":  0.000000000000,"y": -0.886146218183,"z": -0.626600000000},
                        ]
        }
    geo_dict = {'h2': H2, 'h4': H4, 'li': Li, 'o2': O2, 'h2o': H2O, 'ch4': CH4}
    return geo_dict[geo_name]

@sdk.workflow
def benchmarking_project():
    """Workflow that generates random samples and fits them using a linear
    regression."""
    # parameter input
    mol_name = 'h2'
    n_pno = 4
    maxrank = 2
    pyscf_method = 'ccsd(t)'
    geometry = geometry_def(mol_name)

    # compute mra-pno 1 and 2 body integrals from madness
    mol, madmolecule = run_madness(geometry, n_pno, frozen_core=True, name=mol_name, maxrank=maxrank)

    # compute energy from pyscf
    result = compute_pyscf_energy(mol, method=pyscf_method)

    return (madmolecule, result)

if __name__ == "__main__":
    benchmarking_project()
