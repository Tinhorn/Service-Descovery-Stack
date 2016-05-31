import logging
import subprocess
import threading

from utils import nginxconfutils
from utils import utils


class ChangeNginxThread(threading.Thread):
    def __init__(self, thread_id: str, payload: dict, confloc: str, lock: threading.Lock):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("EnginXLink")
        self.thread_id = thread_id
        self.payload = payload
        self.confLoc = confloc
        self.lock = lock

    def run(self):

        logger = self.logger
        thread_id = self.thread_id
        payload = self.payload

        self.lock.acquire(blocking=True)

        nginxconfparser = nginxconfutils.NginxConfUtils(confloc=self.confLoc, thread_id=self.thread_id)
        logger.info("Starting Thread {} with payload \n {}".format(thread_id, utils.pretty_print_json(payload)))

        # Create
        if self.payload_direction(payload=payload):

            key = payload["node"]["key"].split("/")
            value = payload["node"]["value"].split(";")

            service = key[2]
            version = "v" + value[1]

            upstream_name = "{}_{}".format(service, version)
            logger.info("{} upstream name is {}".format(self.thread_id, upstream_name))

            upstream_directive = nginxconfparser.find_upstream_directive(name=upstream_name)

            if upstream_directive is None:
                upstream_directive = nginxconfparser.create_upstream_directive(name=upstream_name)

            nginxconfparser.add_server_to_upstream(upstream_contents=upstream_directive[1], server=value[0])
        #Delete
        else:

            key = payload["node"]["key"].split("/")
            value = payload["prevNode"]["value"].split(";")

            service = key[2]
            version = "v" + value[1]

            upstream_name = "{}_{}".format(service, version)
            logger.info("{} upstream name is {}".format(self.thread_id, upstream_name))

            upstream_directive = nginxconfparser.find_upstream_directive(name=upstream_name)

            #Remove upstream directive
            if upstream_directive is not None:
                nginxconfparser.del_server_from_upstream(upstream_contents=upstream_directive[1], server=value[0])
                nginxconfparser.remove_upstream_if_empty(upstream_directive=upstream_directive)

        nginxconfparser.push_conf()

        subprocess.run("service nginx reload", shell=True)

        self.lock.release()

    def payload_direction(self, payload: dict) -> bool:
        logger = self.logger
        if "action" in payload.keys():
            if payload["action"] == "set":
                logger.info("{}: The payload is create".format(self.thread_id))
                return True
            elif payload["action"] == "expire":
                logger.info("{}: The payload is delete".format(self.thread_id))
                return False
