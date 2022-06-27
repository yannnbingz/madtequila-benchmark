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
    #dependency_imports=[PYSCF_IMPORT],
    custom_image="yannnbingz/m1-madness-tequila:amd64",
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
    result = compute_pyscf_energy()

    return (result,)

if __name__ == "__main__":
    benchmarking_project()
