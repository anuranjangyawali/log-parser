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
    parser.add_argument("--error", "-e", help="output error logs only", action="store_true", dest='perrs')
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
        print(f"File `{source}` not found.")
        sys.exit(1)
    except PermissionError:
        print(f"File `{source}` is not readable.")
        sys.exit(1)

    return parsed_logs


def all_errors(parsed_logs):
    error_logs = [errors for errors in parsed_logs if "error" in errors["Message"].lower()]
    return error_logs


def prog_logs(parsed_logs, program):
    logs = [logs for logs in parsed_logs if logs["Program"].lower() == program.lower()]
    return logs


def prog_errors(error_logs, program):
    prog_error_logs = [p_e_l for p_e_l in error_logs if p_e_l["Program"].lower() == program]
    return prog_error_logs


def write_to_file(path, parsed_logs, error_logs): 
    log_file = "logs.json"
    err_file = "errors.json"

    try:
        if os.path.isdir(path):
            log_file = f"{path}/{log_file}"
            err_file = f"{path}/{err_file}"
            with open(log_file, "w+", encoding="utf-8") as pars:
                json.dump(parsed_logs, pars, indent=4)
            with open(err_file, "w+", encoding="utf-8") as errf:
                json.dump(error_logs, errf, indent=4)
        else:
            print(f"{path} is not a directory")
    except PermissionError:
        print(f"{path} is not writeable.")
        sys.exit(1)


def print_logs(logs):
    print(json.dumps(logs, indent=4))


if __name__ == "__main__":
    args = arg_parse()
   
    parsed_logs = log_parser(args.source)
    error_logs = all_errors(parsed_logs) 

    if args.program: 
        prog_error_logs = prog_errors(error_logs, args.program)
        print_logs(prog_error_logs)

    elif args.path:
        write_to_file(args.path, parsed_logs, error_logs)

    elif args.perrs:
        print_logs(error_logs)

    else:
        print_logs(parsed_logs)

