import os
import pytest

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
MAJOR_VERSION = os.getenv("VERSION").split('.')[0]

RPM_PACKAGES = [
    f'percona-postgresql{MAJOR_VERSION}-server', 'percona-postgresql-common',
    f'percona-postgresql{MAJOR_VERSION}-contrib', f'percona-pg-stat-monitor%{MAJOR_VERSION}',
    'percona-pgaudit', f'percona-pg_repack{MAJOR_VERSION}', f'percona-wal2json{MAJOR_VERSION}'
]
DEB_PACKAGES = ['']


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_package_is_installed(host, package):
    ds = host.system_info.distribution
    if ds.lower() in ["redhat", "centos", 'rhel']:
        pytest.skip("This test only for Debian based platforms")
    pkg = host.package(package)
    assert pkg.is_installed


@pytest.mark.parametrize("package", RPM_PACKAGES)
def test_rpm_package_is_installed(host, package):
    with host.sudo():
        ds = host.system_info.distribution
        if ds in ["debian", "ubuntu"]:
            pytest.skip("This test only for RHEL based platforms")
        pkg = host.package(package)
        assert pkg.is_installed
