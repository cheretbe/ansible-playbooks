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
    print("inv molecule converge --scenario backuppc-xs")


@invoke.task
def test(context):
    """Run all tests"""
    scenarios = test_utils.get_molecule_scenarios(context)
    filtered = ["backuppc", "backuppc-xs", "rsync-bpc", "apache"]
    scenarios = [scenario for scenario in scenarios if scenario not in filtered]
    for scenario in scenarios:
        for driver in ["docker", "lxd"]:
            platform = "linux" if scenario == "failing" else "ubuntu"
            header_text = f"Molecule test {scenario} ({driver})"
            test_utils.print_header(header_text)
            test_utils.run_molecule(context, "test", scenario, driver, platform)
            test_utils.print_success_message(header_text)


@invoke.task(optional=['scenario, driver'])
def molecule(
        context, command, scenario=None, driver="docker"
):
    """Run custom Molecule command"""
    platform = "linux" if scenario == "failing" else "ubuntu"
    test_utils.run_molecule(context, command, scenario, driver, platform=platform)
