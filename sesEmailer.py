# Handles sending the email.

# Generic python goodness about sending emails:  https://realpython.com/python-send-email/
# Since I'm going with Amazon's SES then this is more useful:
#   https://boto3.amazonaws.com/v1/documentation/api/latest/guide/ses-template.html

import boto3
import logging

SOURCE_EMAIL = "beryl@amazon.com"
CHARSET = "UTF-8"

def prettyLocation(l):
    if l == "North America (NA)":
        return "NA"
    if l == "Asia Pacific (APAC)":
        return "APAC"
    if l == "Europe (EU)":
        return "EU"
    return l


def sendMatchEmail(m, p):
    logging.info(f"sendMatchEmail - on enter; topic; {m.topic}, leader: {m.leader}, participants: {m.participants}.")
    leaderLogin = m.leader
    leaderName = p[leaderLogin].firstName
    leaderLocation = p[leaderLogin].location

    participantNames = [p[participant].firstName for participant in m.participants ]
    participantNames.append(leaderName)
    allNames = ", ".join(participantNames)
    skillName = m.topic

    matchees = ""
    for participant in m.participants:
        person = p[participant]
        matchees += f" * {person.firstName}, {prettyLocation(person.location)}\n"

    messageBody = f"""
Hi {allNames},

You have been matched for the skill “{skillName}". {leaderName} ({leaderLogin}@, {prettyLocation(leaderLocation)}) will be your facilitator for the discussion and will schedule a meeting on Learning Day. Thank you for participating and I hope you will find this valuable. Please take some time to get to know each other and most importantly have fun and be engaged!

Matchee(s):
{matchees}

beryl.
"""
    participantsEmailAddresses = [ f"{participant}@amazon.com" for participant in m.participants ]
    participantsEmailAddresses.append(f"{leaderLogin}@amazon.com" )
    
    logging.info(f"Sending to participantsEmailAddresses: {participantsEmailAddresses}")
    logging.info(f"messageBody:\n{messageBody}----\n")

    # Override for the test
    # participantsEmailAddresses = [ "mchughj@gmail.com" ]
    # logging.info(f"Setting override of participantsEmailAddresses to be {participantsEmailAddresses}")

    # Create SES client
    ses = boto3.client('ses')

    response = ses.send_email(
      Source=SOURCE_EMAIL,
      Destination={
        'ToAddresses': participantsEmailAddresses,
        'BccAddresses': [
            "beryl@amazon.com",
        ]
      },
      Message={
        'Body': {
            'Text': {
                'Charset': CHARSET,
                'Data': messageBody,
            },
        },
        'Subject': {
            'Charset': CHARSET,
            'Data': "Your Learning Day Match",
        },
      },
    )
    logging.info(f"sendEmail - done;  recipients: {participantsEmailAddresses}, reponse: {response}")
    logging.info(f"----")
    
