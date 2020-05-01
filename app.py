import os
import requests
import toml
from prometheus_client import start_http_server, Gauge
from time import sleep


CONF_PATH = os.environ.get('CONF_PATH', '/config.toml')
FREQUENCY = int(os.environ.get('FREQUENCY', 43200))
PORT = int(os.environ.get('PORT', 8080))
SOCKET_REST_TOKEN = os.environ['TOKEN']
DEBUG = os.environ.get('DEBUG', False)

if DEBUG:
    print('Loaded')


class RuntimeError(exception):
    pass


class Service(object):
    def __init__(self, domain, port, token=None):
        self.domain = domain
        self.port = port
        self.token = token

    def request(self):
        raise NotImplemented()


class CodeBeautify(Service):
    def request(self):
        x = requests.post(
            "https://codebeautify.org/iptools/openPortChecker",
            data={
                'port': self.port,
                'domain': self.domain
            }
        )
        return x.json()[0] == 'Open'


class SocketRest(Service):
    def request(self):
        x = requests.post(
            "http://socket-rest.vader.dersand.net",
            params = {
                "port": self.port,
                "domain": self.domain,
                "token": self.token
            }
        )
        if x.json().get('error'):
            raise RuntimeError("SocketRest: Token incorrect")
        return x.json().get('status') == 'Online'


def test_port(domain, port):
    return SocketRest(domain, port, SOCKET_REST_TOKEN).request()


def read_conf():
    with open(CONF_PATH) as o:
        return toml.loads(o.read())


def check(error_metric, metric, config):

    for job, obj in config['servers'].items():
        domain = obj['domain']
        port = obj['port']

        try:
            if test_port(domain, port):
                metric.labels(job, domain, port).set(1)
            else:
                metric.labels(job, domain, port).set(0)
            error_metric.set(0)
            if DEBUG:
                print('All fine and dandy')
        except RuntimeError as e:
            print(str(e))
            exit(1)
        except Exception as e:
            if DEBUG:
                print(str(e))
            error_metric.set(1)
            metric.labels(job, domain, port).set(0)

        sleep(1)


def prometheus_metrics():
    return (
        Gauge('port_check_error_count', 'Error'),
        Gauge(
            'port_check_services', 'Status of ports',
            ['service_name', 'domain', 'port']
        )
    )


if __name__ == '__main__':
    print(f'Starting a server on {PORT}')
    start_http_server(PORT)

    config = read_conf()
    error_metric, metric = prometheus_metrics()
    error_metric.set(0)

    while True:
        check(error_metric, metric, config)
        if DEBUG:
            print('Sleeping')
        sleep(FREQUENCY)
