"""
Main used in code ocean to execute capsule
"""

import json
import logging
import os
import subprocess
from glob import glob

from aind_ccf_reg import register

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s : %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    handlers=[
        logging.StreamHandler(),
        # logging.FileHandler("test.log", "a"),
    ],
)
logging.disable("DEBUG")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def save_string_to_txt(txt: str, filepath: str, mode="w") -> None:
    """
    Saves a text in a file in the given mode.

    Parameters
    ------------------------
    txt: str
        String to be saved.

    filepath: PathLike
        Path where the file is located or will be saved.

    mode: str
        File open mode.

    """

    with open(filepath, mode) as file:
        file.write(txt + "\n")


def read_json_as_dict(filepath: str) -> dict:
    """
    Reads a json as dictionary.

    Parameters
    ------------------------

    filepath: PathLike
        Path where the json is located.

    Returns
    ------------------------

    dict:
        Dictionary with the data the json has.

    """

    dictionary = {}

    if os.path.exists(filepath):
        with open(filepath) as json_file:
            dictionary = json.load(json_file)

    return dictionary


def execute_command_helper(command: str, print_command: bool = False) -> None:
    """
    Execute a shell command.

    Parameters
    ------------------------
    command: str
        Command that we want to execute.
    print_command: bool
        Bool that dictates if we print the command in the console.

    Raises
    ------------------------
    CalledProcessError:
        if the command could not be executed (Returned non-zero status).

    """

    if print_command:
        print(command)

    popen = subprocess.Popen(
        command, stdout=subprocess.PIPE, universal_newlines=True, shell=True
    )
    for stdout_line in iter(popen.stdout.readline, ""):
        yield str(stdout_line).strip()
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, command)


def main() -> None:
    """
    Main function to register a dataset
    """
    data_folder = os.path.abspath("../data/")
    processing_manifest_path = glob(f"{data_folder}/processing_manifest_*")[0]

    if not os.path.exists(processing_manifest_path):
        raise ValueError("Processing manifest path does not exist!")

    pipeline_config = read_json_as_dict(processing_manifest_path)

    logger.info(
        f"Processing manifest {pipeline_config} provided in path {processing_manifest_path}"
    )

    results_folder = (
        f"../results/ccf_{pipeline_config['registration']['channel']}"
    )

    # Setting parameters based on pipeline
    example_input = {
        "input_data": f"../data/{pipeline_config['registration']['input_data']}",
        "input_channel": pipeline_config["registration"]["channel"],
        "input_scale": pipeline_config["registration"]["input_scale"],
        "bucket_path": "aind-open-data",
        "reference": os.path.abspath(
            "../data/ccf_atlas_image/ccf_atlas_reference_25_um.tiff"
        ),
        "reference_res": 25,
        "output_data": os.path.abspath(f"{results_folder}/OMEZarr"),
        "metadata_folder": os.path.abspath(f"{results_folder}/metadata"),
        "downsampled_file": "downsampled.tiff",
        "downsampled16bit_file": "downsampled_16.tiff",
        "affine_transforms_file": os.path.abspath(
            f"{results_folder}/affine_transforms.mat"
        ),
        "warp_transforms_file": os.path.abspath(
            f"{results_folder}/warp_transforms.nii.gz"
        ),
        "ls_ccf_warp_transforms_file": os.path.abspath(
            f"{results_folder}/ls_ccf_warp_transforms.nii.gz"
        ),
        "ccf_ls_warp_transforms_file": os.path.abspath(
            f"{results_folder}/ccf_ls_warp_transforms.nii.gz"
        ),
        "code_url": "https://github.com/AllenNeuralDynamics/aind-ccf-registration",
        "ants_params": {"spacing": (14.4, 14.4, 16), "unit": "microns"},
        "OMEZarr_params": {
            "clevel": 1,
            "compressor": "zstd",
            "chunks": (64, 64, 64),
        },
    }

    logger.info(f"Input parameters in CCF run: {example_input}")
    # flake8: noqa: F841
    image_path = register.main(example_input)


if __name__ == "__main__":
    main()
