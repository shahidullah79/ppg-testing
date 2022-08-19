import os

import testinfra.utils.ansible_runner


testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']).get_hosts('all')


def test_patroni(host):
    assert host.service("etcd").is_running
    assert host.service("patroni").is_running, print(host.run("systemctl status patroni").stdout)
    assert host.service("patroni1").is_running, print(host.run("systemctl status patroni1").stdout)
    assert host.service("patroni2").is_running, print(host.run("systemctl status patroni2").stdout)
    print(host.run("ps aux | grep haproxy").stdout)
    print(host.run("cat /etc/haproxy/haproxy.cfg").stdout)
    print(host.run("ps aux | grep postgres").stdout)
    # with host.sudo("postgres"):
    select = 'cd && psql --host localhost --port 5000 postgres -U postgres -c "select version()"'
    result = host.run(select)
    print(result.stdout)
    assert result.rc == 0, result.stderr


