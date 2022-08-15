import orquestra.sdk.v2.dsl as sdk


THIS_IMPORT = sdk.GitImport(
    repo_url="git@github.com:yannnbingz/madtequila-benchmark.git",
    git_ref="main",
)

CUSTOM_IMAGE = "jgonthier/madtequila:latest"

@sdk.task(
    source_import=THIS_IMPORT,
    custom_image=CUSTOM_IMAGE,
    resources=sdk.Resources(cpu='8000m',memory='60Gi', disk='20Gi')
)
def run_pyscf(atom, basis, **kwargs):
    import pyscf
    from pyscf import cc
    mol = pyscf.M(
        atom = atom, 
        basis = basis
    )
    mol.max_memory = 50000
    hf = mol.HF().run()
    ccsd = hf.CCSD()
    ccsd.kernel()
    energy = ccsd.e_tot
    ecorr = ccsd.ccsd_t()
    return energy, ecorr


@sdk.workflow
def get_ccsdt_from_pyscf():

    # parameter input: simple He test
    atom = 'C 0.0 0.0 0.0; O 0.0 0.0 1.1602; O 0.0 0.0 -1.1602'
    basis = 'ccpv5z'


    # compute mra-pno 1 and 2 body integrals from madness
    energy, ecorr = run_pyscf(
                                atom=atom,
                                basis=basis,
    )

    return (energy, ecorr)


if __name__ == "__main__":
    benchmarking_project()
