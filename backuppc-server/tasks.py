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


@invoke.task(test_regular, test_failing)
def test(context):
    """Run all tests"""
