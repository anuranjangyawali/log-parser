#! /usr/bin/env python3

import re
import json
import jq

def main():
    logfile = '/home/zen/parsed-log.json'
    syslog = '/var/log/syslog'
    errorsFile = '/home/zen/errors.json'

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

    with open(logfile, 'w+', encoding="utf-8") as pars:
        json.dump(parsed_logs, pars, indent=4)
    
    with open(errorsFile, 'w+', encoding="utf-8") as errf:
        json.dump(errors, errf, indent=4)

if __name__ == '__main__':
    main()




