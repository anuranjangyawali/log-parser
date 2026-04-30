#! /usr/bin/env python3

import re
import json
import argparse
import os
import sys

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


def log_parser(source):
    reobj = re.compile(
        r"(^[a-z]{3}\s+[0-9]+\s+[0-9:]+)"
        r"\s+([a-z0-9-]+)\s+([a-z0-9_.-]+)"
        r"(?:\[(\d+)])?:\s+(.*)$",
        re.I
    )
    try:
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
    except FileNotFoundError:
        print(f"File `{args.source}` not found.")
        sys.exit(1)
    except PermissionError:
        print(f"File `{args.source}` is not readable.")
        sys.exit(1)

    return parsed_logs

def filter_logs(parsed_logs):
    error_logs = []
    for logs in parsed_logs:
        if "error" in logs["Message"].lower():
            error_logs.append(logs)
    return error_logs

def write_to_file(path, logs, errors):
    log_file = "logs.json"
    err_file = "errors.json"

    try:
        if os.path.isdir(path):
            log_file = f"{path}/{log_file}"
            err_file = f"{path}/{err_file}"
            with open(log_file, "w+", encoding="utf-8") as pars:
                json.dump(logs, pars, indent=4)
            with open(err_file, "w+", encoding="utf-8") as errf:
                json.dump(errors, errf, indent=4)
        else:
            print(f"{path} is not a directory")
    except PermissionError:
        print(f"{path} is not writeable.")
        sys.exit(1)


def log_search(error_logs):
    program_error_logs = []
    for logs in error_logs:
        if logs["Program"].lower() == args.program.lower():
            program_error_logs.append(logs)
    print(json.dumps(program_error_logs, indent=4))


def print_logs():
    logs = log_parser()
    print(json.dumps(logs, indent=4))


def print_err_logs(errors):
    print(json.dumps(errors, indent=4))


if __name__ == "__main__":
    args = arg_parse()

    logs = log_parser(args.source)
    errors = filter_logs(logs)

    if args.program: 
        log_search(errors)
    elif args.isset_e: 
        print_err_logs(errors)
    elif args.path: 
        write_to_file(args.path, logs, errors)
    else: 
        print_logs()

