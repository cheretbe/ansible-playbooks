import sys
import os

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

# pylint: disable=no-member

def test_default_system_locale(host, pytestconfig):
    expected_lang = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="linux_locale_default_lang",
        param_value=pytestconfig.getoption("default_lang"),
        default_value="en_US.UTF-8"
    )
    expected_lc = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="linux_locale_default_LC",
        param_value=pytestconfig.getoption("default_lc"),
        default_value="en_US.UTF-8"
    )

    locale_data = {}
    for line in host.check_output('sudo su - ansible-test -c "locale"').splitlines():
        lc_name, lc_value = line.split("=")
        locale_data[lc_name] = lc_value.replace('"', "")

    assert locale_data["LANG"] == expected_lang

    for lc_parameter in ("LC_NUMERIC", "LC_TIME", "LC_MONETARY", "LC_PAPER",
        "LC_NAME", "LC_ADDRESS", "LC_TELEPHONE", "LC_MEASUREMENT", "LC_IDENTIFICATION"
    ):
        assert locale_data[lc_parameter] == expected_lc
