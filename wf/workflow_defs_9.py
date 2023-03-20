import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:zapatacomputing/vqe-meas-benchmark.git",
    git_ref="main",
)

CUSTOM_IMAGE = "jgonthier/madtequila:latest"


@sdk.task(
    source_import=THIS_IMPORT,
    custom_image=CUSTOM_IMAGE,
    resources=sdk.Resources(cpu="34000m", memory="60Gi", disk="20Gi"),
)
def run_madness(name, geometry, n_pno, frozen_core=True, maxrank=None, **kwargs):
    import tequila as tq
    
    results_dict = {}
    try:
        mol = tq.Molecule(
            name=name,
            geometry=geometry,
            frozen_core=frozen_core,
            n_pno=n_pno,
            maxrank=maxrank,
            **kwargs
        )
        print("*** MOL OBJECT DEFINED, INTEGRALS GENERATED ***")

        with open(name + "_pnoinfo.txt", "r") as f:
            for line in f.readlines():
                if "nuclear_repulsion" in line:
                    nuclear_repulsion = float(line.split("=")[1])
                elif "pairinfo" in line:
                    pairinfo = line.split("=")[1].split(",")
                    # pairinfo = [tuple([int(i) for i in x.split(".")]) for x in pairinfo]
                elif "occinfo" in line:
                    occinfo = line.split("=")[1].split(",")
                    occinfo = [float(x) for x in occinfo]
        h, g = mol.read_tensors(name=name)
        results_dict["nuclear_repulsion"] = nuclear_repulsion
        results_dict["pairinfo"] = pairinfo
        results_dict["occinfo"] = occinfo

    except tq.quantumchemistry.madness_interface.TequilaMadnessException:
        mol = None
        h = None
        g = None

    inputfile = ""
    with open("input", "r") as f_input:
        for line in f_input.readlines():
            inputfile += line
    outfile = ""
    with open(name + "_pno_integrals.out", "r") as f_output:
        for line in f_output.readlines():
            outfile += line

    results_dict["name"] = name
    results_dict["n_pno"] = n_pno
    results_dict["maxrank"] = maxrank
    results_dict["inputfile"] = inputfile
    results_dict["outfile"] = outfile

    return mol, results_dict, h, g

@sdk.task(
    source_import=THIS_IMPORT,
    custom_image=CUSTOM_IMAGE,
    resources=sdk.Resources(cpu="8000m", memory="60Gi", disk="20Gi"),
    #n_outputs=1,
)
def compute_pyscf_energy(mol, method="fci", **kwargs):
    from tequila.quantumchemistry.pyscf_interface import QuantumChemistryPySCF

    try: 
        print("***CALLING PYSCF***")
        mol2 = QuantumChemistryPySCF.from_tequila(mol)
        energy = mol2.compute_energy(method)
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

    except: 
        results_dict = None
e
    return results_dict

@sdk.workflow(data_aggregation=sdk.DataAggregation(resources=sdk.Resources(memory="30Gi", disk="20Gi")))
def benchmarking_project():

    mol_name = "ch4"

    n_pno = 110
    maxrank = 36
    frozen_core = False
    geometry = "C 0.0 0.0 0.0 \n H 0.886146218183 0.0 0.6266 \n H -0.886146218183 0.0 0.6266 \n H 0.0 0.886146218183 -0.6266 \n H 0.0 -0.886146218183 -0.6266"

    pyscf_method = 'ccsd(t)'

    # compute mra-pno 1 and 2 body integrals from madness
    mol, madmolecule, h, g = run_madness(
        name=mol_name,
        geometry=geometry,
        n_pno=n_pno,
        frozen_core=frozen_core,
        maxrank=maxrank,
    )

    # compute energy from pyscf
    result = compute_pyscf_energy(mol, method=pyscf_method)

    return (madmolecule, result, h, g)

if __name__ == "__main__":
    benchmarking_project()