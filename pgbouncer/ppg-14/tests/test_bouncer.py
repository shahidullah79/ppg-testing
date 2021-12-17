import os
import pytest

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')

CREATE_USER = [
    "psql -X -o /dev/null -p $PG_PORT -c \"create user pswcheck with superuser createdb password 'pgbouncer-check';\" p0 || exit 1",
	"psql -X -o /dev/null -p $PG_PORT -c \"create user someuser with password 'anypasswd';\" p0 || exit 1",
	"psql -X -o /dev/null -p $PG_PORT -c \"create user maxedout;\" p0 || exit 1",
	"psql -X -o /dev/null -p $PG_PORT -c \"create user longpass with password '$long_password';\" p0 || exit 1",
    "psql -X -o /dev/null -p $PG_PORT -c \"set password_encryption = on; create user muser1 password 'foo';\" p0 || exit 1",
    "psql -X -o /dev/null -p $PG_PORT -c \"set password_encryption = on; create user muser2 password 'wrong';\" p0 || exit 1",
    "psql -X -o /dev/null -p $PG_PORT -c \"set password_encryption = on; create user puser1 password 'foo';\" p0 || exit 1",
    "psql -X -o /dev/null -p $PG_PORT -c \"set password_encryption = on; create user puser2 password 'wrong';\" p0 || exit 1"
    ]


@pytest.fixture
def create_test_users(host):
    with host.sudo("postgres"):
        for user in CREATE_USER:
            host.run(user)


#def test_pgbouncer(host, create_test_users):
def test_pgbouncer(host):
    with host.sudo("postgres"):
        result = host.run('PATH="/usr/pgsql-14/bin/:$PATH" && cd /tmp/pgbouncer && make check')
        print(result.stdout)
        if result.rc != 0:
            print(result.stderr)
            raise AssertionError


