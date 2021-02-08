import json
import threading
import paramiko
from libs.logger import LogOperation
from libs.config_cache import ConfigCache


class SSHServer(paramiko.ServerInterface):
    client_ip = None
    client_port = None
    client_id = None
    __log_writer = None
    __config_cache = None

    def __init__(self, client_address, in_client_id=str()):
        self.event = threading.Event()
        self.client_address = client_address
        self.client_ip = client_address[0]
        self.client_port = client_address[1]
        self.client_id = in_client_id
        self.__conf_cache = ConfigCache()
        self.__log_writer = LogOperation()
        self.__credentials = dict(json.loads(self.__conf_cache.get_value('ssh', 'credentials')))

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if username.strip() in self.__credentials:
            if self.__credentials.get(username.strip()) == password:
                self.__log_writer.log_info(
                    "{} - {} client {} user is connected".format(self.client_id, self.client_ip, username)
                )
                return paramiko.AUTH_SUCCESSFUL
            else:
                self.__log_writer.log_warning(
                    "{} - {} client {} user password failed ..".format(self.client_id, self.client_ip, username)
                )
        return paramiko.AUTH_FAILED

    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        return True

    def check_auth_interactive_response(self, responses):
        return paramiko.AUTH_FAILED

    def check_auth_interactive(self, username, submethods):
        return paramiko.AUTH_FAILED

    def check_channel_exec_request(self, channel, command):
        clean_cmd = bytes(command).decode('utf8', 'ignore').strip()
        if clean_cmd == '':
            return False
        else:
            print_cmd = clean_cmd
            blank_split = clean_cmd.split(" ")
            if blank_split:
                if blank_split.__len__() > 1:
                    print_cmd = clean_cmd.split(" ")[0]
            message = bytes('{}: {}\r\n'.format(print_cmd, self.__conf_cache.get_value('messages', 'cmd_not_found')).encode())
            channel.send(message)
            self.__log_writer.log_info('{} - {} client entered to command : {} '.format(
                self.client_id, self.client_ip, clean_cmd)
            )
            channel.close()
            return True
