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


def test_pgrepack(host):
    with host.sudo("postgres"):
        mkdir = host.run("mkdir -p /var/lib/postgresql/testts")
        assert mkdir.rc == 0
        ts = host.run("psql -c \"create tablespace testts location '/var/lib/postgresql/testts'\"")
        assert ts.rc == 0
        result = host.run("cd /tmp/pg_repack && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(result.stderr)
            print(result.stdout)
            print(host.file("/tmp/pg_repack/regress/regression.diffs").content_string)
            raise AssertionError


def test_pg_stat_monitor(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/pg_stat_monitor && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(result.stderr)
            print(result.stdout)
            print(host.file("/tmp/pg_stat_monitor/regression.diffs").content_string)
            raise AssertionError
