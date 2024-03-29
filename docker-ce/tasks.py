import os
import sys
import invoke

sys.path.append(os.path.dirname(__file__) + "/../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error


@invoke.task(default=True)
def show_help(context):
    """This help message"""
    context.run('invoke --list')

    print("\nExamples:")
    print("inv test")
    print("inv molecule list --driver lxd")


@invoke.task
def test(context):
    """Run all tests"""
    for scenario in test_utils.get_molecule_scenarios(context):
        for driver in ["docker", "lxd"]:
            header_text = f"Molecule test {scenario} ({driver})"
            test_utils.print_header(header_text)
            test_utils.run_molecule(context, "test", scenario, driver, platform="ubuntu")
            test_utils.print_success_message(header_text)


@invoke.task(optional=['scenario, driver'])
def molecule(
        context, command, scenario=None, driver="docker"
):
    """Run custom Molecule command"""
    test_utils.run_molecule(context, command, scenario, driver, platform="ubuntu")
