import logging
import threading
from datetime import datetime

from utils import utils


class ChangeNginxThread(threading.Thread):
    def __init__(self, thread_id, payload):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("EnginXLink")
        self.thread_id = thread_id
        self.payload = payload

    def run(self):
        logger = self.logger
        thread_id = self.thread_id
        payload = self.payload

        #Block
        logger.info("Starting Thread {} at {}".format(thread_id, datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        logger.info(utils.pretty_print_json(payload))
