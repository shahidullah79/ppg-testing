import os
import pytest

import testinfra.utils.ansible_runner

from .. import settings
testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

RPM_PACKAGES = [
    f'percona-postgresql{settings.MAJOR_VER}-server', 'percona-postgresql-common',
    f'percona-postgresql{settings.MAJOR_VER}-contrib', f'percona-pg_stat_monitor{settings.MAJOR_VER}',
    f'percona-pgaudit{settings.MAJOR_VER}', f'percona-pg_repack{settings.MAJOR_VER}', f'percona-wal2json{settings.MAJOR_VER}'
]
DEB_PACKAGES = [
    f'percona-postgresql-{settings.MAJOR_VER}', 'percona-postgresql-common',
    f'percona-postgresql-contrib', f'percona-pg-stat-monitor{settings.MAJOR_VER}',
    f'percona-postgresql-{settings.MAJOR_VER}-pgaudit', f'percona-postgresql-{settings.MAJOR_VER}-repack',
    f'percona-postgresql-{settings.MAJOR_VER}-wal2json'
]


@pytest.mark.parametrize("package", DEB_PACKAGES)
def test_deb_package_is_installed(host, package):
    ds = host.system_info.distribution
    if ds.lower() in ["redhat", "centos", "rhel", "rocky", "ol"]:
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
