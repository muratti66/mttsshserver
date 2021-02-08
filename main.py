import socketserver
from libs.config_cache import ConfigCache
from libs.ssh_handler import SSHHandler
from libs.logger import LogOperation


if __name__ == '__main__':
    config_cache = ConfigCache()
    sock_ip = config_cache.get_value('socket', 'ip')
    sock_port = int(config_cache.get_value('socket', 'port'))
    ssh_server = socketserver.ThreadingTCPServer((sock_ip, sock_port), SSHHandler)
    LogOperation().log_info('mttSshServer started..')
    ssh_server.serve_forever()
