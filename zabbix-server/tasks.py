"""zabbix-server role tests"""
# pylint: disable=import-error
import invoke
# pylint: enable=import-error


@invoke.task(default=True)
def show_help(context):
    """This help message"""
    context.run('invoke --list')


@invoke.task
def test_default_version(context):
    """Test role without specifying Zabbix version"""
    print(f"Invoke: === {test_default_version.__doc__} ===")
    context.run("molecule test")


# @invoke.task
# def test_version_4_0(context):
#     """Test role with Zabbix version 4.0"""
#     print(f"Invoke: === {test_version_4_0.__doc__} ===")
#     context.run(
#         "molecule test",
#         env={
#             "TEST_ZABBIX_VERSION": "4.0",
#             "EXPECTED_ZABBIX_VERSION": "4.0"
#         }
#     )


@invoke.task
def test_version_4_4(context):
    """Test role with Zabbix version 4.4"""
    print(f"Invoke: === {test_version_4_4.__doc__} ===")
    context.run(
        "molecule test",
        env={
            "TEST_ZABBIX_VERSION": "4.4",
            "EXPECTED_ZABBIX_VERSION": "4.4"
        }
    )


# pylint: disable=unused-argument
@invoke.task(test_default_version, test_version_4_4)
def test(context):
    """Run all tests"""
