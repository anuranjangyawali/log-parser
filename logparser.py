#! /usr/bin/env python3

import re
import json
import argparse
import os

def arg_parse():
    parser = argparse.ArgumentParser(
            description=("A commandline utility that parses syslogd logs. " 
                         "It produces two \'.json\' files \'errors.json\' and \'logs.json\'. " 
                         "The files contain json object list of all parsed logs and json object" 
                         "list of parsed errors logs respectively."),
            prog="logparser"
            )

    parser.add_argument("source", nargs="?" , help="Syslog file path", type=str , default="/var/log/syslog")
    parser.add_argument("--error", "-e", help="output error logs only", action="store_true", dest='isset_e')
    parser.add_argument("--find", "-f", help="output error logs of a specific program only", dest='program')
    parser.add_argument("--output", "-o", help="write logs to the specified directory", nargs='?',\
            const="./", dest='path')

    args = parser.parse_args() 

    return args


# Regex: 1 = timestamp, 2 = hostname, 3 = program, 4 = PID (optional), 5 = message


def log_parser():
    reobj = re.compile(
        r"(^[a-z]{3}\s+[0-9]+\s+[0-9:]+)"
        r"\s+([a-z0-9-]+)\s+([a-z0-9_.-]+)"
        r"(?:\[(\d+)])?:\s+(.*)$",
        re.I
    )
    with open(args.source, 'r', encoding="utf-8") as syslg:
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

    return (parsed_logs, error_logs)


def write_to_file(path):
    log_file = "logs.json"
    err_file = "erros.json"

    if not os.path.isdir(path):
        log_file = path.__add__(log_file)
        err_file = path.__add__(err_file)
    elif os.path.isdir(path):
        log_file = path.__add__('/' + log_file)
        err_file = path.__add__('/' + err_file)

    get_logs = log_parser()
    with open(log_file, "w+", encoding="utf-8") as pars:
        json.dump(get_logs[0], pars, indent=4)
    with open(err_file, "w+", encoding="utf-8") as errf:
        json.dump(get_logs[1], errf, indent=4)



def log_search():
    error_logs = log_parser()
    program_error_logs = []
    for logs in error_logs[1]:
        if logs["Program"].lower() == args.program.lower():
            program_error_logs.append(logs)
    print(json.dumps(program_error_logs, indent=4))


def print_logs():
    get_logs = log_parser()
    print(json.dumps(get_logs[0], indent=4))


def print_err_logs():
    get_logs = log_parser()
    print(json.dumps(get_logs[1], indent=4))


if __name__ == "__main__":
    args = arg_parse()
    if args.program: log_search()
    elif args.isset_e: print_err_logs()
    elif args.path: write_to_file(args.path)
    else: print_logs()

