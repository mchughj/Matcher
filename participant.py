import logging
import math
import match
from dataclasses import dataclass, field
from typing import List
from collections import defaultdict

@dataclass(frozen=True)
class Participant:
    login: str
    firstName: str
    location: str
    interests: List = field(default_factory=list)
    competencies: List = field(default_factory=list)

def parse(line):
    logging.debug(f"parse - start; line: {line}")
    (_, login, firstName, _, _, location, cList, iList ) = line.split(",")

    allInterests = iList.split(";")
    allCompetencies = cList.split(";")

    allCompetencies = list(filter(lambda x: not (x=="None" or x==""), allCompetencies))

    # Yes it is valid to be both competent in things and also to be looking for 
    # help in some way.  But the dataset is so constrained that we need competent people
    # to step forward and not show these people as unassigned. 
    logging.debug(f"login: {login}, allInterests: {allInterests}")
    allInterests = list(filter(lambda x: not (x=="None" or x=="" or x in allCompetencies), allInterests))
    logging.debug(f"After filter login: {login}, allInterests: {allInterests}")
    logging.debug(f"---")

    logging.debug(f"location: {location}")

    return Participant(login, firstName, location, allInterests, allCompetencies)

@dataclass(frozen=True)
class PossibleMatch:
    topic: str
    leaders: List = field(default_factory=list)
    participants: List = field(default_factory=list)

def scoreEvaluationViaMostConstrainedTopic(possibleMatch, allPossibleMatches):
    # The score of a possible match here is comprised of two elements.  
    #
    # The first is how large the group size is.  When the group size is large
    # then we are matching the most constraining need first.
    #
    # If the group size is the same then a score is created based on the leaders
    # and how many possible matches, within the allPossibleMatches, they appear in
    # as leaders.  This value is negated because we want the inverse of that.
    #
    # We compute the second one first.
    #
    totalMatchesForLeadersOfPossibleMatch = 0
    for l in possibleMatch.leaders:
        for m in allPossibleMatches:
            if l in m.leaders:
                totalMatchesForLeadersOfPossibleMatch += 1

    if len(possibleMatch.leaders) > 0:
        return (len(possibleMatch.participants) / len(possibleMatch.leaders), -totalMatchesForLeadersOfPossibleMatch)
    else:
        return (0, -totalMatchesForLeadersOfPossibleMatch)

# This scoring funcion proved to be less useful.
def scoreEvaluationViaRawParticipants(possibleMatch):
    return len(possibleMatch.participants)

def extractAllTopics(participants):
    result = []
    for p in participants:
        result.extend(p.interests)
        result.extend(p.competencies)

    # I want uniques only so turn the list (with duplicates) into a set.
    return set(result)

def buildAllPossibleMatches(allPeople, assignedParticipants, assignedLeaders, topicsRemaining):
    result = []
    for t in topicsRemaining:
        topicLeaders = []
        topicParticipants = []
        for p in allPeople:
            if t in p.competencies and assignedLeaders[p.login] == False:
                topicLeaders.append(p.login)
            elif t in p.interests and assignedParticipants[p.login] == False:
                topicParticipants.append(p.login)
        result.append(PossibleMatch(t, topicLeaders, topicParticipants))
    return result

# breakParticipantsIntoGroups will take a list of size p and a group size - which is a 
# real number - and break the participants into sizes of at most groupSize.  When the 
# list cannot be evenly divided by groupSize - that is when the groupSize has a partial
# component - then this method generates goodness in terms of the distribution.
def breakParticipantsIntoGroups(p, groupSize):
    result = []

    c = 0
    priorStop = 0
    while c < len(p):
        nextResult = []
        nextStop = priorStop + groupSize
        while c < nextStop and c < len(p):
            nextResult.append(p[c])
            c += 1
        priorStop = nextStop

        if len(nextResult) > 0:
            result.append(nextResult)

    total = 0
    for x in result:
        for y in x:
            total += 1
    assert total == len(p)

    return result

# createGroupingsViaConstrainedLeaders - or cgvcl - creates matches that focus
# on matching people to leaders where the most constrained skills are assigned
# first.  A "constrained" skill is one where there are a lot of people who
# want to learn about that skill relative to the number of leaders available to
# teach it.
#
def createGroupingsViaConstrainedLeaders(allPeople, location, groupings, unassigned):
    logging.info(f"cgvcl - on enter; allPeople: {len(allPeople)}")

    # If we are given a location then remove anyone not in that location.
    if location != "":
        allPeople = list(filter( lambda x: x.location == location, allPeople))
        logging.info(f"cgvcl - after filterning for location; allPeople: {len(allPeople)}")

    peopleLookup = dict()
    for x in allPeople:
        peopleLookup[x.login] = x

    topicsRemaining = extractAllTopics(allPeople)
    logging.info(f"cgvcl - determined topics; topicsRemaining: {topicsRemaining}")

    assignedParticipants = defaultdict(lambda: False)
    assignedLeaders = defaultdict(lambda: False)

    while len(topicsRemaining) > 0:
        logging.info(f"cgvcl - beginning another loop; allPeople: {len(allPeople)}, "
                f"assignedParticipants: {len(list(filter(lambda x: assignedParticipants[x], assignedParticipants)))}, "
                f"assignedLeaders: {len(list(filter(lambda x: assignedLeaders[x], assignedParticipants)))}, "
                f"topicsRemaining: {topicsRemaining}")

        possibleMatches = buildAllPossibleMatches(allPeople, assignedParticipants, assignedLeaders, topicsRemaining)
        possibleMatches = sorted(possibleMatches, key=lambda x : scoreEvaluationViaMostConstrainedTopic(x, possibleMatches))

        logging.debug(f"cgvcl - ---- possible matches");
        for x in possibleMatches:
            logging.debug(f"   Score: {scoreEvaluationViaMostConstrainedTopic(x, possibleMatches)}, match: {x}")
        logging.debug(f"cgvcl - ---- end of possible matches");

        # The last one in the possibleMatches is the most constrained
        winner = possibleMatches[-1]

        logging.info(f"cgvcl - winner; score: {scoreEvaluationViaMostConstrainedTopic(winner, possibleMatches)}, winner: {winner}")

        # We are handling this topic so remove it from the list of remaining topics
        topicsRemaining = list(filter(lambda x: x != winner.topic, topicsRemaining))

        if len(winner.participants) == 0:
            logging.info(f"cgvcl - fortunately the winner has no participants so skipping topic;")
            continue
        if len(winner.leaders) == 0:
            logging.info(f"cgvcl - unfortunately winner has no leaders but does have participants; participants: {winner.participants}")
            continue

        leaders = sorted(winner.leaders, key = lambda x: peopleLookup[x].location )
        participants = sorted(winner.participants, key = lambda x: peopleLookup[x].location )

        # For every leader we will grab some number of participants and create a new grouping.
        groupSize = len(participants) / len(leaders)
        participantGroupList = breakParticipantsIntoGroups(participants, groupSize)

        if len(participantGroupList) != len(leaders):
            logging.info( f"Participants broken up into n groups must have the same number as leaders; participants: {len(participants)}, leaders: {len(leaders)}, groupSize: {groupSize}, participantGroupList: {len(participantGroupList)}")

        assert len(participantGroupList) == len(leaders) or len(participants) < len(leaders), "Participants broken up into n groups must have the same number as leaders; "
        
        logging.info(f"cgvcl - creating groupings; topic: {winner.topic}, groupSize: {groupSize}, leaders: {leaders}, participantGroups: {participantGroupList}")

        # zip automatically handles if the leaders have more members in it than the participantGroupList.   Extra leaders are ignored.
        for l,p in zip(leaders, participantGroupList):
            m = match.Match(winner.topic, l, location, p)
            groupings[m.leader] = m

            assignedLeaders[l] = True
            for individualP in p:
                assignedParticipants[individualP] = True

    logging.info(f"cgvcl - done with all loops; allPeople: {len(allPeople)}, "
            f"assignedParticipants: {len(list(filter(lambda x: assignedParticipants[x], assignedParticipants)))}")

    # Look for unassigned participants
    unassigned.extend( list(filter( lambda x: not assignedParticipants[x.login], allPeople)))

    logging.info(f"cgvcl - done; groupings: {len(groupings.keys())}, unassigned len: {len(unassigned)}, unassigned: {unassigned}")

