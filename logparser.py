#! /usr/bin/env python3

import re
import json
import argparse

logFile = './parsed-log.json'
errorsFile = './errors.json'

parser = argparse.ArgumentParser(
        description=("A commandline utility that parses syslogd logs. " 
                     "It produces two \'.json\' files \'errors.json\' and \'parsed-logs.json\'. " 
                     "The files contain json object list of parsed logs and json object" 
                     "list of parsed logs with erros respectively."),
        prog="logparser"
        )

parser.add_argument("source", nargs="?" , help="path to your syslog file", type=str , default="/var/log/syslog")
parser.add_argument("--search","-s", nargs=1, help="outputs error messages of given program name")
args = parser.parse_args() 

source = args.source
searchProgram = args.search


# Regex: 1 = timestamp, 2 = hostname, 3 = program, 4 = PID (optional), 5 = message
def logParser():
    reobj = re.compile(
        r"(^[a-z]{3}\s+[0-9]+\s+[0-9:]+)"
        r"\s+([a-z0-9-]+)\s+([a-z0-9_.-]+)"
        r"(?:\[(\d+)])?:\s+(.*)$",
        re.I
    )
    with open(source, 'r', encoding="utf-8") as syslg:
        parsed_logs = []
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
        error_logs = []
        for logs in parsed_logs:
            for k,v in logs.items():
                if v == None: continue
                if "error" in v.lower(): error_logs.append(logs)
    return ( parsed_logs, error_logs )


def writeToFile():
    gLogs = logParser()
    with open(logFile, 'w+', encoding="utf-8") as pars:
        json.dump(gLogs[0], pars, indent=4)
    with open(errorsFile, 'w+', encoding="utf-8") as errf:
        json.dump(gLogs[1], errf, indent=4)


def logSearch():
    eLogs = logParser()
    pErrorLogs = []
    for logs in eLogs[1]:
        if logs["Program"].lower() == searchProgram[0].lower():
            pErrorLogs.append(logs)
    print(json.dumps(pErrorLogs))


def printLogs():
    gLogs = logParser()
    print(json.dumps(gLogs[0]))


def printErrLogs():
    gLogs = logParser()
    print(json.dumps(gLogs[1]))


if __name__ == "__main__":
    if searchProgram: 
        logSearch()
    else: 
        printLogs()

