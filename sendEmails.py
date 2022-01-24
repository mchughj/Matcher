#
# This script is responsible for kicking off all of the match emails that are found 
# in the pre-generated results.  Use: 
#
#   rm pregen-*
#   python app.py 
#
# to pre-generate the results.  Then browse the results using localhost:4044.  
# 
# Once you are happy with it then use this to send all the emails.

import os
import re
import logging
import participant
import match
import sesEmailer
import sys
import time

from collections import defaultdict

logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

if __name__ == '__main__':
    groupings = dict()
    participants = []

    (matches, peoples) = match.readMatchAndPeopleFiles()
    if len(matches) <= 0:
        logging.info(f"no matches!!")
        sys.exit(1)

    for m in matches:
        groupings[m.leader] = m
    participants.extend(peoples)

    logging.info(f"just read in matches and participants; matches: {len(groupings.keys())}, participants: {len(participants)}")

    p = dict()
    for x in participants:
        p[x.login] = x

    numberSent = 0
    for m in groupings.values():
        if False:
            sesEmailer.sendMatchEmail(m,p)
        else:
            logging.info("Not sending the email.   You must override this if you want to actually send.")

        numberSent += 1
        time.sleep(5)

