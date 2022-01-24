
# Matcher 

A simple set of scripts that helps connect people who are interested in learning about things with those who are proficient.  

## Getting started

In the below if your default 'python' is any version of python greater than 3.7 then change the below commands to just be 'python'.
You must use python 3.7 or beyond so that the @dataclass works.

1. Install necessary prerequisites
   ```
   sudo apt install -y python3.7
   python3.7 -m pip install --user --upgrade pip
   python3.7 -m pip install --user virtualenv
   ```
1. Create a new virtual environment within the same directory as the git repository.
   ```
   python3.7 -m virtualenv --python=python3.7 env
   ```
1. Activate the new virtual environment
   ```
   source env/bin/activate
   ```
1. Install, into the new virtual environment, the required python modules for this specific environment.  This will be installed within the virtual env which was activated earlier.
   ```
   python3.7 -m pip install -r requirements.txt
   ```
1. Ensure that you have AWS credentials stored in ```~/.aws/credentials```.  Really just follow the directions found in https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#installation.  This is necessary to send the emails.
1. Finally, start the server process here
   ```
   python app.py
   ```
   Do not run the flask webserver using the flask executable - this won't pick up the necessary dependencies and you will be forced to install the requirements outside of the virtual env as well as inside of it.


When you run the server process (python app.py) the program will run the matching algorithm and generate two text files 'pregen-matches.txt' and 'pregen-peoples.txt'.  These files will be used upon next invocation.  You can perform overrides to these files in order to change any matchings.  In order to regenerate matches from scratch just remove these two files before running the app.py.

## Sending emails

There is a separate script for sending the emails.  Use with care.

## Using the server

The server process uses port 4044 so visit http://localhost:4044/
