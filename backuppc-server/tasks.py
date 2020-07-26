import invoke
import colorama


def assert_text_in_stderr(run_result, text):
    assert any(text in s for s in run_result.stderr.splitlines()), \
        f"Unexpected error message: stderr does not contain text '{text}'"


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

def do_upgrade_test(
        context, from_backuppc_version, from_backuppc_xs_version=None,
        from_backuppc_rsync_bpc_version=None
    ):

    from_version_env = {"TEST_BACKUPPC_VERSION": from_backuppc_version}
    if not from_backuppc_xs_version is None:
        from_version_env.update({"TEST_BACKUPPC_XS_VERSION": from_backuppc_xs_version})
    if not from_backuppc_rsync_bpc_version is None:
        from_version_env.update({"TEST_BACKUPPC_RSYNC_BPC_VERSION": from_backuppc_rsync_bpc_version})

    print_sub_header(f"Install version {from_backuppc_version}")
    run_command(context, "molecule destroy -s default")
    run_command(
        context,
        "molecule converge -s default",
        env=from_version_env
    )
    run_command(
        context,
        "molecule idempotence -s default",
        env=from_version_env
    )
    run_command(
        context,
        "molecule verify -s default",
        env={"EXPECTED_BACKUPPC_VERSION": from_backuppc_version}
    )

    print_sub_header("Upgrade to the latest version")
    run_command(context, "molecule converge -s default")
    run_command(context, "molecule idempotence -s default")
    run_command(
        context,
        "molecule verify -s default",
        env={"EXPECTED_BACKUPPC_VERSION": "latest"}
    )
    run_command(context, "molecule destroy -s default")


@invoke.task(default=True)
def show_help(context):
    """This help message"""
    context.run('invoke --list')

    print("Examples:")
    print("inv test-upgrade-from-version 4.3.1 0.59 3.1.2.1")


@invoke.task
def test_regular(context):
    """Test regular role run"""
    print_header(test_regular.__doc__)
    run_command(context, "molecule test -s default")
    print_success_message(test_regular.__doc__)


@invoke.task
def test_upgrade(context):
    """Test regular role run and then an upgrade"""
    print_header(test_upgrade.__doc__)

    do_upgrade_test(context=context, from_backuppc_version="4.3.1")

    print_success_message(test_upgrade.__doc__)


@invoke.task
def test_upgrade_from_version(
        context, backuppc_version, backuppc_xs_version, backuppc_rsync_version
    ):
    """Test upgrade from a specific version to the latest one"""
    print_header(test_upgrade.__doc__)

    do_upgrade_test(
        context=context,
        from_backuppc_version=backuppc_version,
        from_backuppc_xs_version=backuppc_xs_version,
        from_backuppc_rsync_bpc_version=backuppc_rsync_version
    )


@invoke.task
def test_data_directory(context):
    """Test data directory creation"""

    print_header(test_data_directory.__doc__)

    print_sub_header("prepare_no_backuppc_dir.yml")
    # backuppc_server_custom_data_dir parameter is not set
    # The role should create /var/lib/backuppc and set is as a home directory
    # for backuppc-server user
    run_command(
        context,
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir.yml",
            "TESTINFRA_FILTER": "test_no_custom_dir"}
    )

    print_sub_header("prepare_no_backuppc_dir_custom_data_dir.yml")
    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc does
    # not exist, custom data directory exists
    # The role should create /var/lib/backuppc as a symlink to the custom data
    # directory, set is as a home directory for backuppc-server user and set
    # correct permissions on custom data directory
    run_command(
        context,
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir_custom_data_dir.yml",
            "TEST_DATA_DIR": "/custom/data/dir",
            "TESTINFRA_FILTER": "test_custom_dir"}
    )

    print_sub_header("prepare_no_backuppc_dir_no_custom_data_dir.yml")
    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc does
    # not exist, custom data directory does not exist
    # The role should create /var/lib/backuppc as a symlink to the custom data
    # directory, set is as a home directory for backuppc-server user, create
    # custom data directory and set correct permissions on it
    run_command(
        context,
        "molecule test -s data-dir",
        env={
            "PREPARE_PLAYBOOK": "prepare_no_backuppc_dir_no_custom_data_dir.yml",
            "TEST_DATA_DIR": "/custom/data/dir",
            "TESTINFRA_FILTER": "test_custom_dir"}
    )

    print_sub_header("prepare_backuppc_dir_wrong_symlink.yml")
    # backuppc_server_custom_data_dir parameter is set, /var/lib/backuppc exists
    # as a symlink to directory other than specified custom data directory
    # The role should fail
    run_result = run_command(
        context,
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

    print_success_message(test_data_directory.__doc__)


@invoke.task
def test_failing(context):
    """Test the role failing on non-supported platform"""

    print_header(test_failing.__doc__)

    run_result = run_command(context, "molecule test -s failing", warn=True)

    assert (run_result.return_code != 0), \
        "Molecule converge call is expected to fail"
    assert_text_in_stderr(
        run_result,
        "Only Ubuntu 18.04 is supported at the moment"
    )

    print_success_message(test_failing.__doc__)


@invoke.task(test_regular, test_upgrade, test_data_directory, test_failing)
def test(context):
    """Run all tests"""
