import invoke


def assert_text_in_stderr(run_result, text):
    assert any(text in s for s in run_result.stderr.splitlines()), \
        f"Unexpected error message: stderr does not contain text '{text}'"


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
    context.run(
        "molecule converge -s default",
        env={"TEST_BACKUPPC_VERSION": "4.3.0"}
    )
    context.run(
        "molecule idempotence -s default",
        env={"TEST_BACKUPPC_VERSION": "4.3.0"}
    )
    context.run(
        "molecule verify -s default",
        env={"EXPECTED_BACKUPPC_VERSION": "4.3.0"}
    )

    context.run("molecule converge -s default")
    context.run("molecule idempotence -s default")
    context.run(
        "molecule verify -s default",
        env={"EXPECTED_BACKUPPC_VERSION": "latest"}
    )
    context.run("molecule destroy -s default")


@invoke.task
def test_data_directory(context):
    """Test data directory creation"""

    # backuppc_server_custom_data_dir parameter is not set
    # The role should create /var/lib/backuppc and set is as a home directory
    # for backuppc-server user
    context.run(
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir.yml",
            "TESTINFRA_FILTER": "test_no_custom_dir"}
    )

    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc does
    # not exist, custom data directory exists
    # The role should create /var/lib/backuppc as a symlink to the custom data
    # directory, set is as a home directory for backuppc-server user and set
    # correct permissions on custom data directory
    context.run(
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir_custom_data_dir.yml",
            "TEST_DATA_DIR": "/custom/data/dir",
            "TESTINFRA_FILTER": "test_custom_dir"}
    )

    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc does
    # not exist, custom data directory does not exist
    # The role should create /var/lib/backuppc as a symlink to the custom data
    # directory, set is as a home directory for backuppc-server user, create
    # custom data directory and set correct permissions on it
    context.run(
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir_no_custom_data_dir.yml",
            "TEST_DATA_DIR": "/custom/data/dir",
            "TESTINFRA_FILTER": "test_custom_dir"}
    )

    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc exists
    # as a symlink to directory other than specified custom data directory
    # The role should fail
    run_result = context.run(
        "molecule test -s data-dir",
        warn=True,
        env={
            "PREPARE_PLAYBOOK": "prepare_backuppc_dir_wrong_symlink.yml",
            "TEST_DATA_DIR": "/custom/data/dir",
            "TESTINFRA_FILTER": "test_custom_dir"}
    )
    assert (run_result.return_code != 0), \
        "Molecule converge call is expected to fail"
    assert_text_in_stderr(
        run_result,
        "/var/lib/backuppc exists and is not linked to /custom/data/dir. "
        "Please fix the symlink before continuing."
    )


@invoke.task
def test_failing(context):
    """Test the role failing on non-supported platform"""
    run_result = context.run("molecule test -s failing", warn=True)

    assert (run_result.return_code != 0), \
        "Molecule converge call is expected to fail"
    assert_text_in_stderr(
        run_result,
        "Only Ubuntu 18.04 is supported at the moment"
    )


@invoke.task(test_regular, test_upgrade, test_data_directory, test_failing)
def test(context):
    """Run all tests"""
