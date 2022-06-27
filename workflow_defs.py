import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/madtequila-benchmark.git",
    git_ref="main",
)

TEQUILA_IMPORT = sdk.GitImport(
    repo_url="git@github.com:tequilahub/tequila.git",
    git_ref="devel",
)

PYSCF_IMPORT = sdk.GitImport(
    repo_url="git@github.com:pyscf/pyscf.git",
    git_ref="master",
)


@sdk.task(
    source_import=THIS_IMPORT,
    dependency_imports=[TEQUILA_IMPORT],
    custom_image="jgonthier/madtequila:latest",
    n_outputs=4,
    #resources=sdk.Resources(cpu='6000m', memory='6Gb')
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


@sdk.task(
    source_import=THIS_IMPORT,
    dependency_imports=[PYSCF_IMPORT],
    custom_image="jgonthier/madtequila:latest",
    n_outputs=1
)
def compute_pyscf_energy():
    import pyscf

    mol = pyscf.M(
                    atom = 'H 0 0 0; H 0 0 0.75; H 0.75 0 0; H 0.75 0 0.75 ',
                    basis = 'sto3g'
                    )

    hf = pyscf.scf.RHF(mol)
    hf.kernel()
    print("energy: ", hf.e_tot)

    return hf.e_tot

@sdk.workflow
def benchmarking_project():
    """Workflow that generates random samples and fits them using a linear
    regression."""
    # parameter input
    mol_name = 'he'
    n_pno = 2
    maxrank = 2
    pyscf_method = 'hf'
    frozen_core=False
    geometry = 'he 0.0 0.0 0.0'

    # compute mra-pno 1 and 2 body integrals from madness
    mol, madmolecule, h, g = run_madness( name=mol_name, 
                                    geometry=geometry, 
                                    n_pno=n_pno, 
                                    frozen_core=frozen_core, 
                                    maxrank=maxrank
                                    )

    # compute energy from pyscf
    result = compute_pyscf_energy()

    return (madmolecule, result)

if __name__ == "__main__":
    benchmarking_project()
