import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pgaudit(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/pg_audit && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(result.stderr)
            print(result.stdout)
            print(host.file("/tmp/pg_audit/regression.diffs").content_string)
            raise AssertionError


