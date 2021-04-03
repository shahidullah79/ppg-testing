import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pgbouncer(host):
    with host.sudo("postgres"):
        result = host.run('PATH="/usr/pgsql-12/bin/:$PATH" && cd /tmp/pgbouncer && make check')
        print(result.stdout)
        if result.rc != 0:
            print(result.stderr)
            raise AssertionError


