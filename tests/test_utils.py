import pathlib
import invoke
import colorama
import yaml

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

def get_base_config_path(lxd=False):
    if lxd:
        base_config = "molecule/molecule_base_lxd_linux.yml"
    else:
        base_config = "molecule/molecule_base_docker_linux.yml"
    return str(pathlib.Path(__file__).resolve().parent / base_config)

def get_molecule_scenarios(context):
    scenarios = []
    for child_obj in (pathlib.Path.cwd() / "molecule").iterdir():
        if child_obj.is_dir():
            if (child_obj / "molecule.yml").exists():
                scenarios.append(child_obj.name)
    return scenarios


def run_molecule(context, command, scenario=None, lxd=False):
    molecule_command = f"molecule --base-config {get_base_config_path(lxd)} {command}"
    if scenario is not None:
        molecule_command += f" -s {scenario}"
    run_command(context, molecule_command)
