import logging
from enum import Enum

from utils import nginxparser


# Dict will be a directive i.e {"http":"{'server':["line"]}"}
# Start of a line will be preceded by on

class NginxConfUtils:
    def __init__(self, confloc: 'str', thread_id: 'str'):
        self.logger = logging.getLogger("EnginXLink")
        self.confloc = confloc
        self.thread_id = thread_id
        self.parsed_conf = None
        self.http_content = None

        self.load_conf()

    def push_conf(self):
        nginxparser.dump(_file=open(file=self.confloc, mode='w'), blocks=self.parsed_conf)

    def load_conf(self):
        self.parsed_conf = nginxparser.load(open(file=self.confloc))

        http_directive = self.parsed_conf[len(self.parsed_conf) - 1]
        self.http_content = http_directive[1]

    def add_server_to_upstream(self, upstream_contents: list, server: str):
        self.logger.info("{}: Adding {} to {}".format(self.thread_id, server, upstream_contents))
        server_directive = ["server", server]
        upstream_contents.insert(len(upstream_contents), server_directive)
        self.logger.info("{}: Added \n {}".format(self.thread_id, upstream_contents))

    def del_server_from_upstream(self, upstream_contents: list, server: str):
        self.logger.info("{}: Removing {} from {}".format(self.thread_id, server, upstream_contents))
        for directive in upstream_contents:
            if server in directive:
                self.logger.debug(
                    "{}: Found {} at {}".format(self.thread_id, server, upstream_contents.index(directive)))
                upstream_contents.remove(directive)
        self.push_conf()
        self.load_conf()

    def create_upstream_directive(self, name: str):
        self.logger.info("{}: Creating upstream {}".format(self.thread_id, name))
        upstream_directive = [['upstream', name], []]

        self.http_content.insert(len(self.http_content) - 1, upstream_directive)

        return upstream_directive

    def remove_upstream_if_empty(self, upstream_directive: list):
        self.logger.info("{}: Checking to remove {}".format(self.thread_id, upstream_directive))

        if len(upstream_directive) == 0:
            self.http_content.remove(upstream_directive)
        else:
            count = self.len_of_server_directive(upstream_contents=upstream_directive[1])
            if count == 0:
                self.logger.info("{}: {} Removed".format(self.thread_id, upstream_directive))
                self.http_content.remove(upstream_directive)

    def find_upstream_directive(self, name: str):

        for directive in self.http_content:
            if name in directive[0]:
                self.logger.debug("{}: Returning {}".format(self.thread_id, directive))
                return directive
            self.logger.debug("{}: Upstream directive: ".format(self.thread_id, directive))
        return None

    def len_of_server_directive(self, upstream_contents: list):
        self.logger.info("{}: Counting {}".format(self.thread_id, upstream_contents))
        server_count = 0
        for directive in upstream_contents:
            if "server" in directive:
                server_count += 1
        self.logger.debug("{}: Count: {}".format(self.thread_id, server_count))
        return server_count

    def change_load_balance_type(self, upstream_content: list, lb_type: int):
        logger = self.logger

        current_lb_type = upstream_content
        result_lb_type = LoadBalanceType(lb_type)

        logger.info("{}: Changing {} to {}".format(self.thread_id, current_lb_type, result_lb_type.name))

        if len(upstream_content) == 0:
            upstream_content.append("directive_placeholder")
        # Round Robin
        if lb_type == 3:
            if "server" not in upstream_content[0]:
                del upstream_content[0]
        else:
            if "server" in upstream_content[0]:
                upstream_content.insert(0, [result_lb_type.name])
            else:
                upstream_content[0] = [result_lb_type.name]

        logger.info("{}: Changed Directive: {}".format(self.thread_id, upstream_content))

    def printconf(self):
        logging.info(self.parsed_conf)


class LoadBalanceType(Enum):
    ip_hash = 1
    least_conn = 2
    round_robin = 3
