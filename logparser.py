#! /usr/bin/env python3

import re
import json
import jq
import argparse

logFile = './parsed-log.json'
errorsFile = './errors.json'

parser = argparse.ArgumentParser(
        description=("A commandline utility that parses syslogd logs." 
                     "It produces two \'.json\' files \'errors.json\' and \'parsed-logs.json\'." 
                     "The files contain json object list of parsed logs and json object" 
                     "list of parsed logs with erros respectively."),
        prog="logparser"
        )

parser.add_argument("source", nargs="?" , help="path to your syslog file", type=str , default="/var/log/syslog")
parser.add_argument("--search","-s", nargs=1, help="outputs error messages of given program name")
args = parser.parse_args() 

source = args.source
searchProgram = args.search


def logParser():
    syslog = source

    # Regex:
    # 1 = timestamp
    # 2 = hostname
    # 3 = program
    # 4 = PID (optional)
    # 5 = message

    reobj = re.compile(
        r"(^[a-z]{3}\s+[0-9]+\s+[0-9:]+)"
        r"\s+([a-z0-9-]+)\s+([a-z0-9_.-]+)"
        r"(?:\[(\d+)])?:\s+(.*)$",
        re.I
    )

    parsed_logs = []

    with open(syslog, 'r', encoding="utf-8") as syslg:
        for line in syslg:
            reggy = reobj.search(line)
            
            if not reggy:
                continue

            parsed_logs.append({
                'Timestamp': reggy.group(1),
                'Hostname': reggy.group(2),
                'Program': reggy.group(3),
                'PID': reggy.group(4),
                'Message': reggy.group(5)
                })

    errors = jq.compile('.[] | select( .Message | test("error"; "i"))').input(parsed_logs).all()

    with open(logFile, 'w+', encoding="utf-8") as pars:
        json.dump(parsed_logs, pars, indent=4)
    
    with open(errorsFile, 'w+', encoding="utf-8") as errf:
        json.dump(errors, errf, indent=4)

    print(json.dumps(parsed_logs))


def logSearch():

    with open(errorsFile, "r", encoding="utf-8") as errs2:
        errors2 = json.load(errs2)
    messages = jq.compile('.[] | select ( .Program | test($program; "i"))', args={"program": searchProgram[0] })\
            .input(errors2).all()
    print(json.dumps(messages))


if searchProgram: 
    logParser()
    logSearch()
else:
    logParser()
