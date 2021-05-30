import multiprocessing
import subprocess
import time
from typing import List

Method = str
Resp = tuple[float, str]

GET: Method = 'get'
POST: Method = 'post'
PUT: Method = 'put'
DELETE: Method = 'delete'


def run_cmd(cmd: str, cool_down=0) -> Resp:
    """
    Run a single command in a shell subprocess and record both the time table

    :param cmd: the command to execute
    :param cool_down: the period of time to cool down after the command was invoked.
    :return: response containing time taken and stdout string response.
    """
    s = time.time()
    r = subprocess.run(cmd.split(' '), stdout=subprocess.PIPE).stdout.decode('utf-8')
    e = time.time()
    time.sleep(cool_down)
    return s - e, r


def get_uri(path: str, ip: str, port=None) -> str:
    """
    Calculates a CoAP URI path.

    :param path: the path to the resource (e.g. 'temp')
    :param ip: the ip address of the device (e.g. '192.168.1.12')
    :param port: [opt] the port of the device (e.g. '5683')
    :return: calculated CoAP URI.
    """
    port = f':{port}' if port else ''
    path = path[1:] if path.startswith('/') else path
    return f'coap://{ip}{port}/{path}'


def test(method: Method, path: str, ip: str, port=None, timeout=15, payload='', cool_down=0) -> Resp:
    """
    Test a CoAP path and receive the time taken and response received.

    :param method: the CoAP method to use (e.g. PUT)
    :param path: the path to the resource (e.g. 'temp')
    :param ip: the ip address of the device (e.g. '192.168.1.12')
    :param port: [opt] the port of the device (e.g. '5683')
    :param timeout: the period to wait before timeout.
    :param payload: any payload to attach to the requests (useful for requests like PUT).
    :param cool_down: the period of time to cool down after the request was received.
    :return: CoAP response containing time taken and stdout string response.
    """
    uri = get_uri(path, ip, port=port)
    payload = f'-e "{payload}"' if payload else ''
    cmd = f'coap-client -m {method} {uri} -B {timeout} {payload}'
    resp = run_cmd(cmd, cool_down=cool_down)
    return resp


def test_paths(method: Method, paths: List[str], ip: str, **kwargs) -> List[Resp]:
    """
    Test multiple CoAP paths and receive a list of Resp entries containing time taken and response received.

    :param method: the CoAP method to use (e.g. PUT)
    :param paths: the paths to test (e.g. ['temp', 'humid']
    :param ip: the ip address of the device (e.g. '192.168.1.12')
    :param kwargs: the keyword arguments to supply to `test()` function.
    :return:
    """
    return [test(method, path, ip, **kwargs) for path in paths]


def test_times_sync(method: Method, path: str, ip: str, times: int, **kwargs) -> List[Resp]:
    """
    Invoke the test command `times` times synchronously and return list of the responses received.

    :param method: the CoAP method to use (e.g. PUT)
    :param path: the path to the resource (e.g. 'temp')
    :param ip: the ip address of the device (e.g. '192.168.1.12'
    :param times: the number of times to test the path.
    :param kwargs: the keyword arguments to supply to `test()` function.
    :return: list of received responses.
    """
    return [test(method, path, ip, **kwargs) for _ in range(times)]


def test_times_multi(method: Method, path: str, ip: str, times: int, workers=10, **kwargs) -> List[Resp]:
    """
    Invoke the test command `times` times concurrently using `workers` threads and return list of the
    responses received.

    :param method: the CoAP method to use (e.g. PUT)
    :param path: the path to the resource (e.g. 'temp')
    :param ip: the ip address of the device (e.g. '192.168.1.12'
    :param times: the number of times to test the path.
    :param kwargs: the keyword arguments to supply to `test()` function.
    :return: list of received responses.
    """

    def test_helper(_):
        return test(method, path, ip, **kwargs)

    with multiprocessing.Pool(workers) as pool:
        return pool.map(test_helper, range(times))
