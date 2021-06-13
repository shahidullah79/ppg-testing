import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_patroni(host):
    with host.sudo("postgres"):
        select = 'psql --host 127.0.0.1 --port 5000 postgres -c "select version()"'
        assert host.run(select).rc == 0


