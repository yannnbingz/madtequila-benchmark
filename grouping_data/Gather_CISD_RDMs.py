import re
import subprocess


bucket_path = "s3://zapata-zmachine/projects/bp-combustion-project/phase-2/mpea-runtime/data/publication-data/cisd_rdms/"
aws_profile = "--profile zapata-zmachine"
ls_cmd = "aws s3 ls "
cp_cmd = "aws s3 cp "
untar_cmd = "tar zxvf "
tar_cmd = "tar zcvf "


def compress_and_upload(target, result, path=None):
    """Little function to compress a file with tar zcvf and
    upload it to amazon with path appended to the bucket_path
    Args:
        target: the path of the target file to compress and upload
        result: the path where to store the compressed file
        path: Optionally, the subfolder where to upload the file in the
              S3 bucket
    """

    compress_cmd = tar_cmd + result + " " + target
    print(compress_cmd)
    subprocess.check_output(compress_cmd, shell=True)

    upload_cmd = cp_cmd + result + " " + bucket_path + path + " " + aws_profile
    print(upload_cmd)
    subprocess.check_output(upload_cmd, shell=True)


def download_and_uncompress(target):
    """Little function to download a file from AWS S3
    and uncompress it with tar zxvf.
    Args:
        target: The path to append to the bucket path to get the file
    """

    download_cmd = cp_cmd + bucket_path + target + " . " + aws_profile
    print(download_cmd)
    subprocess.check_output(download_cmd, shell=True)

    filename = re.sub(r".*/", "", target)

    uncompress_cmd = untar_cmd + filename
    print(uncompress_cmd)
    subprocess.check_output(uncompress_cmd, shell=True)


# @profile
def main():

    mol_search = re.compile(".*molecule: '([A-Z0-9]*)'")
    act_search = re.compile(".*nactiveorbs: '([A-Z0-9]*)'")
    type_search = re.compile(".*orb-type: '([ A-Za-z0-9]*)'")
    path_search = re.compile(".*hamiltonian: '([^']*)'")
    missing_rdms = set()
    found_rdms = set()
    n_rdms = 0
    with open("hamiltonian_data", "r") as f:
        for line in f:
            match_mol = mol_search.search(line)
            match_act = act_search.search(line)
            match_type = type_search.search(line)
            if match_type:
                n_rdms += 1
                molname = match_mol.group(1)
                nactiveorbs = match_act.group(1)
                orbtype = match_type.group(1)

                if orbtype == "MP2 NOs":
                    orbtype = "NOs"
                newname = molname + "-" + nactiveorbs + "-" + orbtype + "-cisd-rdm.tgz"

                ham_path = path_search.search(line).group(1)
                print(ham_path)
                folder_path = re.sub("hamiltonian.tgz", "", ham_path)
                ls_folder = subprocess.check_output(
                    ls_cmd + "s3://zapata-zmachine/" + folder_path + " " + aws_profile,
                    shell=True,
                )
                if "cisd-rdm" not in str(ls_folder):
                    print(f"CISD RDM missing for {molname}, {nactiveorbs}, {orbtype}.")
                    missing_rdms.add(newname)
                else:
                    found_rdms.add(newname)
                    cisd_cp_cmd = (
                        "aws s3api copy-object --copy-source "
                        + "zapata-zmachine/"
                        + folder_path
                        + "cisd-rdms.tgz"
                        + " --bucket zapata-zmachine --key projects/bp-combustion-project/phase-2/mpea-runtime/data/publication-data/cisd_rdms/"
                        + newname
                        + " "
                        + aws_profile
                    )
                    cp_output = subprocess.check_output(cisd_cp_cmd, shell=True)

    assert len(missing_rdms) + len(found_rdms) == n_rdms
    print("The missing RDMs are:")
    print(missing_rdms)


if __name__ == "__main__":
    main()
