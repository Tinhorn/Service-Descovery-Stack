#!/usr/bin/python

import logging
import sys
from threading import Lock

import requests

from utils import watchetcdutils


# TODO Validate file
def validate_args(argv):
    # make sure there are two arguements
    if len(argv) < 3:
        logger.info("No argument, Have to specify the ip of the instance and file")
        logger.info("python EnginXLink.py 204.204.1.1 /etc/nginx/nginx.conf")
        logger.argv()
        sys.exit(1)

        # Make sure the file exist


def watch_services_node(url, file):
    payload = {'recursive': 'true', 'wait': 'true'}
    while True:
        try:
            r = requests.get(url=url, params=payload)
            return_body = r.json()

            # Checking that return dict is empty
            if return_body:
                watch_thread = watchetcdutils.ChangeNginxThread(confloc=file, thread_id=watchthreadid, payload=return_body,
                                                                lock=thread_lock)
                watch_thread.start()
                # confutils = nginxconfutils.NginxConfUtils(confloc=file, thread_id=watchthreadid)
                # confutils.load_conf()

        except requests.Timeout:
            logger.info("Timeout happened")


def main(argv):
    validate_args(argv)
    url = "http://{}:2379/v2/keys/services".format(argv[1])
    logger.info("Watching {}".format(url))
    #    logger.info("Nginx conf file is at {}".format(target.name()))
    watch_services_node(url=url, file=argv[2])


if __name__ == "__main__":
    logging.basicConfig(filename='enginxlink.log', datefmt='%m-%d %H:%M:%S',
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logger = logging.getLogger("EnginXLink")
    logger.setLevel(logging.INFO)
    watchthreadid = 0
    thread_lock = Lock()
    main(sys.argv)
