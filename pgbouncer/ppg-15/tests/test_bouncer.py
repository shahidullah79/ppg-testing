import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pgbouncer(host):
    with host.sudo("postgres"):
        result = host.run('PATH="/usr/pgsql-15/bin/:$PATH" && cd /var/lib/pgsql/pgbouncer/test && make check')
        # result = host.run('PATH="/usr/pgsql-14/bin/:$PATH" && cd /tmp/pgbouncer/test && ./test.sh')
        print(result.stdout)
        if result.rc != 0:
            print(result.stderr)
            raise AssertionError


