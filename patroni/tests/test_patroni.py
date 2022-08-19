import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_patroni(host):
    assert host.service("etcd").is_running
    print(host.run("journalctl -xe").stdout)
    assert host.service("patroni").is_running, print(host.run("systemctl status patroni").stdout)
    assert host.service("patroni1").is_running, print(host.run("systemctl status patroni1").stdout)
    assert host.service("patroni2").is_running, print(host.run("systemctl status patroni2").stdout)
    with host.sudo("postgres"):
        select = 'cd && psql --host 127.0.0.1 --port 5000 postgres -c "select version()"'
        result = host.run(select)
        print(result.stdout)
        assert result.rc == 0, result.stderr


