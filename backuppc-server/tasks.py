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
    print("inv molecule converge --scenario=backuppc-xs")
    print(
        "inv upgrade --backuppc-from=4.3.2 --backuppc-xs-from=0.59 --rsync-bpc-from=3.0.9.15"
    )
    print(
        "inv upgrade --backuppc-from=4.3.2 --backuppc-xs-from=0.59 --rsync-bpc-from=3.0.9.15 "
        "--backuppc-to=4.4.0 --backuppc-xs-to=0.62 --rsync-bpc-to=3.1.3.0"
    )


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


@invoke.task(optional=['driver'])
def upgrade(
        context,
        backuppc_from, backuppc_xs_from, rsync_bpc_from,
        backuppc_to="latest", backuppc_xs_to="latest", rsync_bpc_to="latest",
        driver="docker"
    ):
    """Run version upgrade test"""
    test_utils.run_molecule(
        context,
        command="test",
        scenario="upgrade",
        driver=driver,
        platform="ubuntu",
        env={
            "TEST_BACKUPPC_FROM": backuppc_from,
            "TEST_BACKUPPC_XS_FROM": backuppc_xs_from,
            "TEST_RSYNC_BPC_FROM": rsync_bpc_from,
            "TEST_BACKUPPC_TO": backuppc_to,
            "TEST_BACKUPPC_XS_TO": backuppc_xs_to,
            "TEST_RSYNC_BPC_TO": rsync_bpc_to
        }
    )

@invoke.task(optional=['scenario, driver'])
def molecule(
        context, command, scenario=None, driver="docker"
):
    """Run custom Molecule command"""
    platform = "linux" if scenario == "failing" else "ubuntu"
    test_utils.run_molecule(context, command, scenario, driver, platform=platform)
