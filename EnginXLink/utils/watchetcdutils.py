import logging
import threading
from datetime import datetime

from utils import utils


class ChangeThread (threading.Thread):

    def __init__(self, threadid, payload):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger("EnginXLink")
        self.thread_id = threadid
        self.payload = payload


    def run(self):
        logger = self.logger
        thread_id = self.thread_id
        payload = self.payload

        logger.info("Starting Thread {} at {}".format(thread_id, datetime.now().strftime('%d/%m/%Y %H:%M:%S')))
        logger.info(utils.pretty_print_json(payload))
