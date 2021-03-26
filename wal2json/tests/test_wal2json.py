import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_wal2json(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/wal2json && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(host.file("/tmp/wal2json/regression.diffs").content)
            raise AssertionError


