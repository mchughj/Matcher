
from datetime import datetime
from flask import Flask, render_template
import os
import re
import logging
import participant
import match
import sesEmailer
import sys

from collections import defaultdict

logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Location for the webserver
serverHost = "0.0.0.0"
serverPort = 4044

participants = []

groupings = dict()
unassigned = []

logging.info(f"Listening to: {serverHost}:{serverPort}")

def readInputFile():
    global participants

    commentLine = re.compile('^\s*#')
    with open("input.txt") as f:
        # Remove the first line as it is the header for the spreadsheet.
        next(f)
        for line in f:
            result = commentLine.search(line)
            if result and result.group(1) != None: 
                print( f"Found comment line: {line}")
                continue

            # Strip any trailing comments from the line
            line = re.sub('#.*$', '', line) 
            line = line.strip()

            p = participant.parse(line)
            if p.login == "Anonymous":
                continue

            # If we already saw the p.login then remove it from the participants list.
            participants = list(filter(lambda x: not x.login == p.login, participants))

            participants.append(p)

    logging.info(f"readInputFile - finished; len of participants: {len(participants)}")

def readPregeneratedResults():
    global participants 
    global groupings 

    (matches, peoples) = match.readMatchAndPeopleFiles()
    if len(matches) > 0:
        for m in matches:
            groupings[m.leader] = m
        participants.extend(peoples)

        logging.info(f"readPregeneratedResults - just read in matches and participants; matches: {len(groupings.keys())}, participants: {len(participants)}")

        # Recreate the unassigned
        for p in participants:
            found = False
            for m in matches:
                if p.login in m.participants:
                    found = True

            if not found:
                unassigned.append(p)

        logging.info(f"readPregeneratedResults - found all unassigned; count: {len(unassigned)}")

        return True
    else:
        logging.info(f"readPregeneratedResults - no file found!")
        return False

def assignPairings():
    participant.createGroupingsViaConstrainedLeaders(participants, "", groupings, unassigned)

@app.route('/')
def root():
    p = dict()
    for x in participants:
        p[x.login] = x

    return render_template("home.html", 
            p = p,
            groupings=groupings, unassigned=unassigned,
            )

if __name__ == '__main__':
    if not readPregeneratedResults():
        readInputFile()
        assignPairings()
        match.writeMatchAndPeopleFiles(groupings.values(), participants)

    app.run(debug=True, host=serverHost, port=serverPort)
