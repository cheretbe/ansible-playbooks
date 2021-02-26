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
    print("inv converge")
    print("inv molecule list -s auto_reboot --lxd")


@invoke.task
def test(context):
    """Run all tests"""
    for scenario in test_utils.get_molecule_scenarios(context):
        for use_lxd in [False, True]:
            driver_name = "lxd" if use_lxd else "docker"
            header_text = f"Molecule test {scenario} ({driver_name})"
            test_utils.print_header(header_text)
            test_utils.run_molecule(context, "test", scenario, use_lxd)
            test_utils.print_success_message(header_text)


@invoke.task
def converge(context):
    """Run Molecule converge using 'default' scenario for Docker"""
    test_utils.run_molecule(context, "converge")


@invoke.task(optional=['scenario, lxd'])
def molecule(
        context, command, scenario=None, lxd=False
):
    """Run custom Molecule command"""
    test_utils.run_molecule(context, command, scenario, lxd)