import paramiko
import socketserver
import time
import random
import string
import subprocess
from libs.config_cache import ConfigCache
from libs.logger import LogOperation
from libs.custom_exception import CustomException
from libs.paramiko_server import SSHServer

# Static variables
BYTE_NR = b'\r\n'
EXIT_CMD = ['reboot', 'shutdown', 'exit', 'logout', 'init']


class SSHHandler(socketserver.StreamRequestHandler):
    chan = None
    client_ip = None
    client_port = None
    client_id = None
    # Library initialize
    __conf_cache = ConfigCache()
    __log_writer = LogOperation()
    # Variables initalize
    __key_file = __conf_cache.get_value('socket', 'key_file')
    __timeout = int(__conf_cache.get_value('socket', 'timeout'))
    __no_answer = int(__conf_cache.get_value('general', 'no_answer'))
    __sleep_between = int(__conf_cache.get_value('general', 'sleep_between'))
    __ssh_version = __conf_cache.get_value('ssh', 'ssh_version')
    __banner = __conf_cache.get_value('ssh', 'banner')
    __ps1_str = '{}:~# '.format(__conf_cache.get_value('ssh', 'hostname')).encode('UTF-8', 'ignore')
    # Command checking and initialisation
    __only_block = True
    __allowed_commands = list(__conf_cache.get_value('ssh', 'allowed_commands'))
    __denied_commands = list(__conf_cache.get_value('ssh', 'denied_commands'))
    if __allowed_commands is None or __allowed_commands.__len__() == 0:
        __only_block = False
    # SSHServer key load
    __host_key = paramiko.RSAKey(filename=__key_file)

    @staticmethod
    def __id_generate(in_size, in_chars=string.ascii_uppercase + string.digits) -> str:
        """
        Id generator
        :param in_size: Size Integer
        :param in_chars: Char Detail
        :return: str
        """
        return ''.join(random.choice(in_chars) for _ in range(in_size))

    def __command_execute(self, command=str()) -> str:
        """
        Command executer for ssh server
        :param command: command str
        :return: standard output
        """
        self.__log_writer.log_debug('Executed : {}'.format(command))
        o = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = o.communicate()
        return_code = o.poll()
        self.__log_writer.log_debug('Output : {}'.format(output.decode('UTF-8', 'ignore').strip()))
        if return_code != 0:
            raise CustomException(error.decode('UTF-8', 'ignore').strip())
        return output.decode('UTF-8', 'ignore').strip()

    @staticmethod
    def __whitespace_prepare(count=int()) -> str:
        """
        Whitespace creator for backspace cleaning on cli.
        :param count: Current word count int
        :return: prepared whitespaces str
        """
        ws_list = list()
        for i in range(count + 30):
            ws_list.append(" ")
        return ''.join(ws_list)

    def read_msg(self) -> str:
        """
        Read entered command string from ssh connection
        :return: entered command str
        """
        if self.__sleep_between != 0:
            time.sleep(self.__sleep_between)
        self.send_msg(message=self.__ps1_str, first_msg=True)
        received_cmd = str()
        while True:
            received_byte = self.chan.recv(1)
            if received_byte == b'\x7f':
                received_cmd = received_cmd[:-1]
                self.chan.sendall('\r' + self.__whitespace_prepare(count=received_cmd.__len__()))
                self.send_msg('\r' + self.__ps1_str.decode('utf-8', 'ignore') + received_cmd, first_msg=False)
                continue
            else:
                self.chan.send(received_byte)
            received = bytes(received_byte).decode('utf8', 'ignore')
            # self.send_msg(message=received, first_msg=False)
            received_cmd += received
            if received == '\n' or received == '\r':
                break
        return received_cmd

    def send_msg(self, message, first_msg=True, multi_line=False) -> None:
        """
        Send messages, output and other responses to client
        :param message: message str
        :param first_msg: if need the newline ? bool
        :param multi_line: if sending multiline data bool
        :return: None
        """
        global BYTE_NR
        if self.__no_answer == 0:
            if multi_line:
                for line in message.splitlines().__iter__():
                    self.chan.send(line.encode())
                    self.chan.send(BYTE_NR)
            elif first_msg:
                self.chan.send(BYTE_NR)
                self.chan.send(message)
            else:
                self.chan.send(message)

    def send_err_msg(self, message, first_msg=True, multi_line=False) -> None:
        """
        Send error messages to client
        :param first_msg: if need the newline ? bool
        :param message: message str
        :param multi_line: if sending multiline data bool
        :return: None
        """
        global BYTE_NR
        if self.__no_answer == 0:
            if multi_line:
                for line in self.__banner.split("\n").__iter__():
                    self.chan.send_stderr(bytes(line.encode()))
                    self.chan.send_stderr(BYTE_NR)
            elif first_msg:
                self.chan.send_stderr(BYTE_NR)
                self.chan.send_stderr(message)
            else:
                self.chan.send_stderr(message)

    def stop_chan(self):
        self.chan.close()

    def __command_control(self, command=str()) -> None:
        """
        Command control with configuration with Exception handling..
        :param command: entered command str
        :return: None
        """
        clear_command = command.split(' ')[0].strip()
        if self.__only_block:
            if clear_command not in self.__allowed_commands:
                raise CustomException('{}: {}'.format(command, self.__conf_cache.get_value('messages', 'cmd_not_allowed')))
        else:
            if clear_command in self.__denied_commands:
                raise CustomException('{}: {}'.format(command, self.__conf_cache.get_value('messages', 'cmd_not_allowed')))

    def handle(self):
        global BYTE_NR, EXIT_CMD
        self.client_id = self.__id_generate(in_size=16)
        self.client_ip = self.client_address[0]
        self.client_port = self.client_address[1]

        self.__log_writer.log_info("{} - {}:{} connected".format(
            self.client_id, self.client_ip, self.client_port)
        )
        try:
            t = paramiko.Transport(self.connection)
            t.handshake_timeout = 5
            t.auth_timeout = 15
            t.banner_timeout = 5
            t.clear_to_send_timeout = 10
            t.local_version = self.__ssh_version
            t.add_server_key(self.__host_key)
            server = SSHServer(self.client_address, in_client_id=self.client_id)
            try:
                t.start_server(server=server)
            except paramiko.SSHException:
                self.__log_writer.log_warning(
                    '{} SSH negotiation failed'.format(self.client_ip)
                )
                return
            t.auth_timeout = self.__timeout
            t.banner_timeout = self.__timeout
            t.clear_to_send_timeout = self.__timeout
            self.chan = t.accept(timeout=self.__timeout)
            server.event.wait(4)
            if self.chan is None:
                self.__log_writer.log_warning(
                    '{} connection not have a any channel'.format(self.client_ip)
                )
                t.close()
                return
            server.event.set()
            if not server.check_channel_shell_request(self.chan):
                self.__log_writer.log_warning(
                    '{} client never asked for a shell'.format(self.client_ip)
                )
                t.close()
                return

            self.send_msg(message=self.__banner, multi_line=True)
            while True:
                received_cmd = self.read_msg().strip()
                try:
                    self.__log_writer.log_debug('{} - {} client entered : {} '.format(
                        self.client_id, self.client_ip, received_cmd))
                    if received_cmd is None:
                        continue
                    elif received_cmd == "":
                        continue
                    elif received_cmd in EXIT_CMD:
                        break
                    # command is allowed ?
                    self.__command_control(command=received_cmd)
                    # command execute
                    out = self.__command_execute(command=received_cmd)
                    if out is not None and out.strip() != "":
                        self.send_msg(message=self.__command_execute(command=received_cmd), multi_line=True)
                except CustomException as e:
                    self.__log_writer.log_warning(in_message=str(e))
                    self.send_err_msg(message=str(e))

            self.chan.send(BYTE_NR)
            self.chan.close()
            t.close()
        except:
            pass
        finally:
            try:
                self.__log_writer.log_info("{} - {}:{} disconnected".format(
                    self.client_id, self.client_ip, self.client_port))
            except:
                pass
