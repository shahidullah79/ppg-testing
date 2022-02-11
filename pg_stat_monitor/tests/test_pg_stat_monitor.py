import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_pg_stat_monitor(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/pg_stat_monitor && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(result.stderr)
            print(result.stdout)
            print(host.file("/tmp/pg_stat_monitor/regression.diffs").content_string)
            raise AssertionError
