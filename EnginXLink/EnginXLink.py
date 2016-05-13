#!/usr/bin/python

import logging
import sys

import requests

from utils import watchetcdutils


#TODO Validate file
def validate_args(argv):
    if len(argv) < 3:
        logging.info("No argument, Have to specify the ip of the instance")
        sys.exit(1)


def watch_services_node(url):
    payload = {'recursive': 'true', 'wait': 'true'}
    r = requests.get(url=url, params=payload)
    watch_thread = watchetcdutils.ChangeThread(threadid=watchthreadid, payload=r.json())
    watch_thread.start()


def main(argv):
    validate_args(argv)
    url = "http://{}:2379/v2/keys/services".format(argv[1])
    logger.info("Watching {}".format(url))
    watch_services_node(url=url)


if __name__ == "__main__":
    logging.basicConfig(filename='enginxlink.log')
    logger = logging.getLogger("EnginXLink")
    logger.setLevel(logging.INFO)
    watchthreadid = 0
    main(sys.argv)
