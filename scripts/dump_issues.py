"""
Script to write out text files containing body of each issue
"""
import sys
import json
import subprocess
import os
import re



if __name__ == '__main__':

    if len(sys.argv) != 2:
        print('Usage:\t{} [directory that does noy exist]'.format(sys.argv[0]))
        print('Purpose:\tExtract content of all issues and write to file')

    output_dir = sys.argv[1]

    if os.path.exists(output_dir):
        print('Directory exists. exiting')
        sys.exit(1)

    os.mkdir(output_dir)

    results = subprocess.check_output('gh issue list -L 3000 --json title,body,state,number,labels'.split())

    data = json.loads(results)

    for i in data:
        match = re.search('\(([A-Za-z0-9.]+)\)$', i['title'])
        if not match:
            print('ERROR: could not interpret "{}"'.format(i['title']))
            continue
        filename = match.groups()[0]
        with open(os.path.join(output_dir, filename), 'w') as fh:
            fh.write(i['body'])

