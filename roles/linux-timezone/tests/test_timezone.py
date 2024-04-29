import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

# pylint: disable=no-member

def test_timezone(host, pytestconfig):
    expected_timezone = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="linux_timezone_name",
        param_value=pytestconfig.getoption("timezone"),
        default_value="Europe/Kaliningrad"
    )

    current_timezone = None
    for line in host.check_output("timedatectl status").splitlines():
        value_name, value = line.split(":", maxsplit=1)
        if value_name.strip() == "Time zone":
            # Here we are look for values like this:
            # Time zone: Europe/Kaliningrad (EET, +0200)
            current_timezone = value.split("(")[0].strip()
    if current_timezone is None:
        raise Exception("Couldn't detect current timezone")
    assert current_timezone == expected_timezone
