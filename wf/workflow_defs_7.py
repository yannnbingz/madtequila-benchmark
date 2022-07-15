import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/madtequila-benchmark.git",
    git_ref="main",
)

TEQUILA_IMPORT = sdk.GitImport(
    repo_url="git@github.com:tequilahub/tequila.git",
    git_ref="devel",
)

CUSTOM_IMAGE = "kottmanj/madness-tequila:v7"

@sdk.task(
    source_import=THIS_IMPORT,
    dependency_imports=[TEQUILA_IMPORT],
    custom_image=CUSTOM_IMAGE,
    #n_outputs=4,
    resources=sdk.Resources(cpu='2000m',memory='2Gi', disk='10Gi')
)
def run_madness(name, geometry, n_pno, frozen_core=True, maxrank=None, **kwargs):
    import tequila as tq
    
    mol = tq.Molecule(
                        name = name,
                        geometry = geometry,
                        frozen_core = frozen_core,
                        n_pno = n_pno,
                        maxrank = maxrank,
                        **kwargs
                        )
    print("*** MOL OBJECT DEFINED, INTEGRALS GENERATED ***")

    with open (name + '_pnoinfo.txt', 'r') as f:
        for line in f.readlines():
            if "nuclear_repulsion" in line:
                nuclear_repulsion = float(line.split("=")[1])
            elif "pairinfo" in line:
                pairinfo = line.split("=")[1].split(",")
                #pairinfo = [tuple([int(i) for i in x.split(".")]) for x in pairinfo]
            elif "occinfo" in line:
                occinfo = line.split("=")[1].split(",")
                occinfo = [float(x) for x in occinfo]

    h, g = mol.read_tensors(name=name)


    results_dict = {}
    results_dict['nuclear_repulsion'] = nuclear_repulsion
    results_dict['pairinfo'] = pairinfo
    results_dict['occinfo'] = occinfo
    results_dict['n_pno'] = n_pno

    return mol, results_dict, h, g


# @sdk.task(
#     source_import=THIS_IMPORT,
#     dependency_imports=[TEQUILA_IMPORT],
#     custom_image=CUSTOM_IMAGE,
#     #n_outputs=1,
# )
# def compute_pyscf_energy(mol, method="fci", **kwargs):
#     from tequila.quantumchemistry.pyscf_interface import QuantumChemistryPySCF

#     print("***CALLING PYSCF***")
#     mol2 = QuantumChemistryPySCF.from_tequila(mol)
#     energy = mol2.compute_energy(method)
#     results_dict = {}
#     results_dict['SCHEMA'] = "schema"
#     results_dict['name'] = mol.parameters.name
#     results_dict['method'] = method
#     results_dict['n_electrons'] = mol.n_electrons
#     results_dict['n_orbitals'] = mol.n_orbitals
#     results_dict['energy'] = energy
#     mra_pno = "({},{})".format(mol.n_electrons, ", ", 2*mol.n_orbitals)
#     print("*** MRA-PNO ***: \n")
#     print(mra_pno)
#     print("*** PYSCF ENERGY: ***\n")
#     print(energy)

#     return results_dict

@sdk.workflow
def benchmarking_project():

    # parameter input: simple He test
    mol_name = 'h2o'
    # mol_name = 'h2o'
    n_pno = 6
    maxrank = 2
    pyscf_method = 'hf'
    frozen_core=False
    geometry = 'h 0.0 0.7547 -0.521394777902 \n h 0.0 -0.7547 -0.521394777902 \n o 0.0 0.0 0.065705222098'
    # geometry= 'h 0.000000000000 0.754700000000 -0.521394777902 \n h 0.000000000000 -0.754700000000  -0.521394777902 \n o 0.000000000000  0.000000000000  0.065705222098'


    # compute mra-pno 1 and 2 body integrals from madness
    mol, madmolecule, h, g = run_madness(   
                                            name=mol_name, 
                                            geometry=geometry, 
                                            n_pno=n_pno, 
                                            frozen_core=frozen_core, 
                                            maxrank=maxrank
                                        )

    # compute energy from pyscf
    # result = compute_pyscf_energy(mol, method=pyscf_method)

    # return (madmolecule, result, h, g)
    return (madmolecule, h, g)


if __name__ == "__main__":
    benchmarking_project()
