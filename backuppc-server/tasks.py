import invoke


@invoke.task(default=True)
def help(context):
    """This help message"""
    context.run('invoke --list')


@invoke.task
def test_regular(context):
    """Test regular role run"""
    context.run("molecule test -s default")


@invoke.task
def test_upgrade(context):
    """Test regular role run and then an upgrade"""
    context.run("molecule destroy -s default")
    context.run("molecule converge -s default",
                env={"TEST_BACKUPPC_VERSION": "4.3.0"}
                )
    context.run("molecule idempotence -s default",
                env={"TEST_BACKUPPC_VERSION": "4.3.0"}
                )
    context.run("molecule verify -s default",
                env={"EXPECTED_BACKUPPC_VERSION": "4.3.0"}
                )

    context.run("molecule converge -s default")
    context.run("molecule idempotence -s default")
    context.run("molecule verify -s default",
                env={"EXPECTED_BACKUPPC_VERSION": "latest"}
                )
    context.run("molecule destroy -s default")

@invoke.task
def test_data_directory(context):
    """Test data directory creation"""
    context.run(
                "molecule test -s data-dir",
                env={
                    "PREPARE_PLAYBOOK": "prepare1.yml",
                    "TESTINFRA_FILTER": "test_dummy1"
                    }
                )


@invoke.task
def test_failing(context):
    """Test the role failing on non-supported platform"""
    context.run("molecule destroy -s failing")
    run_result = context.run("molecule converge -s failing", warn=True)

    assert (run_result.return_code != 0), \
        "Molecule converge call is expected to fail"
    assert any("Only Ubuntu 18.04 is supported at the moment" in s
               for s in run_result.stderr.splitlines()
               ), \
        "Unexpected error message"

    context.run("molecule destroy -s failing")


@invoke.task(test_regular, test_data_directory, test_failing)
def test(context):
    """Run all tests"""
