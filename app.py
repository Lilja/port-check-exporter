import os
import requests
import toml
from prometheus_client import start_http_server, Gauge
from time import sleep


CONF_PATH = os.environ.get('CONF_PATH', './config.toml')
FREQUENCY = os.environ.get('FREQUENCY', 43200)


def test_port(domain, port):
    x = requests.post(
        "https://codebeautify.org/iptools/openPortChecker",
        data={
            'port': port,
            'domain': domain
        }
    )
    return x.json()[0]


def read_conf():
    with open(CONF_PATH) as o:
        return toml.loads(o.read())


def check(metric, config):

    for job, obj in config['servers'].items():
        domain = obj['domain']
        port = obj['port']

        try:
            res = test_port(domain, port)

            if res['status'] == 'Open':
                metric.labels(job, domain, port).set(1)
            else:
                metric.labels(job, domain, port).set(0)
        except Exception:
            metric.labels(job, domain, port).set(0)

        sleep(1)


def prometheus_metrics():
    return Gauge(
        'port_check_services', 'Status of ports',
        ['service_name', 'domain', 'port']
    )


if __name__ == '__main__':
    start_http_server(8000)

    config = read_conf()
    metric = prometheus_metrics()
    while True:
        check(metric, config)
        sleep(FREQUENCY)
