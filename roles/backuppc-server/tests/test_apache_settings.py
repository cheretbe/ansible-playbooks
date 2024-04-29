import sys
import os
import pytest
import apacheconfig

sys.path.append(os.path.dirname(__file__) + "/../../tests")
import test_utils  # pylint: disable=wrong-import-position,import-error

# We don't test files permissions and if modules are enabled, since main backuppc
# status page test will fail anyway if something goes wrong

@pytest.mark.apache
def test_backuppc_conf_file(host, pytestconfig):
    apache_require = test_utils.get_parameter_value(
        host=host,
        ansible_var_name="backuppc_server_apache_require",
        param_value=pytestconfig.getoption("apache_require"),
        default_value="Require all granted"
    ).lower().replace("require ", "")

    with apacheconfig.make_loader() as loader:
        config = loader.loads(
            host.file("/etc/apache2/conf-available/backuppc.conf").content_string
        )
    # BackupPC source code has this trailing space
    cgi_bin_dir = pytestconfig.getoption("cgi_bin_dir") + " "
    module_2_4_plus = next(item for item in config["Directory"][cgi_bin_dir]["IfModule"] if "authz_core_module" in item)
    assert {"Require": [apache_require, "valid-user"]} in module_2_4_plus["authz_core_module"]["RequireAll"]

# TODO: Consider testing backuppc_server_www_users propagation to
# /etc/BackupPC/BackupPC.users
