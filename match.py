
from dataclasses import dataclass, field
from typing import List
import logging
import participant
from os.path import exists


@dataclass(frozen=True)
class Match:
    topic: str
    leader: str
    location: str
    participants: List = field(default_factory=list)

def parseMatch(line):
    (topic, leader, location, pList ) = line.split(",")
    participants = pList.split(";")

    return Match(topic, leader, location, participants)

def writeMatchAndPeopleFiles(matches, allPeople):
    with open("pregen-matches.txt", "w") as f:
        for m in matches:
            f.write(f"{m.topic},{m.leader},{m.location},{';'.join(m.participants)}\n")

    with open("pregen-peoples.txt", "w") as f:
        for p in allPeople:
            f.write(f"UNUSED,{p.login},{p.firstName},UNUSED,UNUSED,{p.location},{';'.join(p.competencies)},{';'.join(p.interests)}\n")

    logging.info(f"writeMatchAndPeopleFiles; match count: {len(matches)}, people count: {len(allPeople)}")


def readMatchAndPeopleFiles():
    matches = []
    allPeople = []

    if exists("pregen-matches.txt"):
        with open("pregen-matches.txt", "r") as f:
            for line in f:
                line = line.strip()
                p = parseMatch(line)
                matches.append(p)
        with open("pregen-peoples.txt", "r") as f:
            for line in f:
                line = line.strip()
                p = participant.parse(line)
                allPeople.append(p)

    logging.info(f"readMatchAndPeopleFiles; match count: {len(matches)}, people count: {len(allPeople)}")
    return (matches, allPeople)


