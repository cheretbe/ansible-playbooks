import pathlib
import enum
import invoke
import colorama

class MoleculeDriver(enum.Enum):
    docker = 1
    lxd = 2
    vagrant = 3

def print_header(header_text):
    print(
        colorama.Fore.CYAN + colorama.Style.BRIGHT +
        f" {header_text} ".center(80, "=") +
        colorama.Style.RESET_ALL
    )


def print_sub_header(sub_header_text):
    print(
        colorama.Fore.CYAN + colorama.Style.BRIGHT + "--" +
        f" {sub_header_text} ".ljust(78, "-") +
        colorama.Style.RESET_ALL
    )


def print_success_message(success_message_text):
    print(
        colorama.Fore.GREEN + colorama.Style.BRIGHT +
        f" {success_message_text}: Success ".center(80, "=") +
        colorama.Style.RESET_ALL
    )


def run_command(context, *args, **kwargs):
    try:
        return context.run(*args, **kwargs)
    except invoke.exceptions.Failure:
        print(
            colorama.Fore.RED + colorama.Style.BRIGHT +
            "Failure: error executing '" + args[0] + "' command" +
            colorama.Style.RESET_ALL
        )
        raise

def get_base_config_path(driver_code):
    if driver_code == MoleculeDriver.lxd:
        base_config = "molecule/molecule_base_lxd_linux.yml"
    elif driver_code == MoleculeDriver.docker:
        base_config = "molecule/molecule_base_docker_linux.yml"
    else:
        base_config = "molecule/molecule_base_vagrant_linux.yml"
    return str(pathlib.Path(__file__).resolve().parent / base_config)

def get_molecule_scenarios(context):
    scenarios = []
    for child_obj in (pathlib.Path.cwd() / "molecule").iterdir():
        if child_obj.is_dir():
            if (child_obj / "molecule.yml").exists():
                scenarios.append(child_obj.name)
    return scenarios


def run_molecule(context, command, scenario, driver):
    driver_code = MoleculeDriver[driver.lower()]
    molecule_env = None
    if driver_code == MoleculeDriver.lxd:
        molecule_env = {"MOLECULE_USER_NAME": "root"}
    elif driver_code == MoleculeDriver.vagrant:
        molecule_env = {"MOLECULE_USER_NAME": "vagrant"}
    molecule_command = f"molecule --base-config {get_base_config_path(driver_code)} {command}"
    if scenario is not None:
        molecule_command += f" -s {scenario}"
    run_command(context, molecule_command, env=molecule_env)
