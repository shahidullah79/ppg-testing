import os

import testinfra.utils.ansible_runner
from ... import settings


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')
MAJOR_VER = settings.MAJOR_VER


def test_pg_stat_monitor(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/pg_stat_monitor && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(result.stderr)
            print(result.stdout)
            print(host.file("/tmp/pg_stat_monitor/regression.diffs").content_string)
            raise AssertionError


def test_pgbouncer(host):
    dist = host.system_info.distribution
    test_dir = "/var/lib/postgresql/pgbouncer"
    bin_dir = f"/usr/lib/postgresql/{MAJOR_VER}/bin/"
    if dist in ['centos', 'rhel', 'redhat']:
        test_dir = "/var/lib/pgsql/pgbouncer"
        bin_dir = f"/usr/pgsql-{MAJOR_VER}/bin/"
    with host.sudo("postgres"):
        result = host.run(
            f"PATH=\"{bin_dir}:/usr/sbin/:$PATH\""
            f" && cd {test_dir} && make check")
        print(result.stdout)
        if result.rc != 0:
            print(result.stderr)
            raise AssertionError


def test_wal2json(host):
    with host.sudo("postgres"):
        result = host.run("cd /tmp/wal2json && make installcheck USE_PGXS=1")
        if result.rc != 0:
            print(host.file("/tmp/wal2json/regression.diffs").content)
            raise AssertionError


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


def test_pgbadger(host):
    with host.sudo():
        result = host.run('cd /tmp/pgbadger && prove')
        print(result.stdout)
        if result.rc != 0:
            print(result.stderr)
            raise AssertionError


# def test_pgbackrest(host):
#     dist = host.system_info.distribution
#     test_dir = "/var/lib/postgresql/pgbackrest"
#     bin_dir = f"/usr/lib/postgresql/{MAJOR_VER}/bin/"
#     if dist in ['centos', 'rhel', 'redhat']:
#         test_dir = "/var/lib/pgsql/pgbackrest"
#         bin_dir = f"/usr/pgsql-{MAJOR_VER}/bin/"
#     with host.sudo("postgres"):
#         result = host.run(
#             f'cd {test_dir} && test/test.pl'
#             f' --pgsql-bin={bin_dir} --log-level-test-file=off'
#             f' --no-coverage-report --module=command --module=storage'
#             f' --vm-host=none --vm-max=2 --vm=none --no-coverage --no-valgrind')
#         print(result.stdout)
#         if result.rc != 0:
#             print(result.stderr)
#             raise AssertionError


