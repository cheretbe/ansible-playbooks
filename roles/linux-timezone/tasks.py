import os
import sys
import invoke

sys.path.append(os.path.dirname(__file__) + "/../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error


@invoke.task(default=True)
def show_help(context):
    """This help message"""
    context.run('invoke --list')

    print(
        "Scenarios: {}".format(
            ", ".join(test_utils.get_molecule_scenarios(context))
        )
    )

    print("\nExamples:")
    print("inv test")
    print("inv molecule list --driver lxd")


@invoke.task
def test(context):
    """Run all tests"""
    test_utils.run_molecule(context, "test", "default", "lxd")


@invoke.task(optional=['scenario, driver'])
def molecule(
        context, command, scenario=None, driver='docker'
):
    """Run custom Molecule command"""
    if driver == "docker":
        raise Exception(
            "Can't run tests under Docker as 'timedatectl status' command will fail\n"
            "(see https://stackoverflow.com/a/46837044 for details)"
        )
    test_utils.run_molecule(context, command, scenario, driver)
