import json
import subprocess
import re
import csv
import sys
import os


def tables_to_dict(text):
    """
    Extract information from tables and return as a dictionary
    """
    
    section = None
    key = None
    
    results = {}
    
    for line in text.split("\n"):
        match = re.search('## (.*)', line)
        if match:
            section = match.group(1).strip()
            if 'STASH' in section:
                section = "STASH entries"
                results[section] = []
            else:
                results[section] = {}
            continue
        if line.startswith("|"):
            linedata = [i.strip().strip("`") for i in line.split("|")]
            if linedata[1] in ['Key', '---', 'Field', 'Model']:
                continue
            if section.startswith("Data") or section.startswith("Mapping"):
                key = linedata[1]
                value = linedata[2]
                results[section][key] = value
            if section.startswith('STASH'):
                model, stash, stash_num, time, dom, usage = linedata[1:7]
                if stash != "":
                    results[section].append({
                        'model': model,
                        'STASH': stash,
                        'stash_number': stash_num,
                        'time_profile': time,
                        'domain_profile': dom,
                        'usage_profile': usage
                        })
    return results
                
                
                


if __name__ == '__main__':

    # location for result files
    output_dir = sys.argv[1]
    
    # obtain results NOTE LIMIT TO 2000
    result = subprocess.check_output('gh issue list -L 2000 --json number,title,body,labels'.split())

    # parse json data
    data = json.loads(result)

    # prepare mappings.json
    results = []
    for entry in data:
        result = tables_to_dict(entry['body'])
        result['title'] = entry['title']
        result['issue_number'] = entry['number']
        result['labels'] = [i['name'] for i in entry['labels']]
        results.append(result)

    with open(os.path.join(output_dir, 'mappings.json'), 'w') as fh:
        json.dump(results, fh, indent=2, sort_keys=True)

    # prepare mappings.csv
    all_mapping_keys = set()
    for entry in results:
        for i in entry['Mapping information']:
            all_mapping_keys.add(i)

    order_first = ['title', 'issue_number']
    order_link = ['link']
    order_labels = ['labels']
    order_dr = sorted(list(results[0]['Data Request information'].keys()))
    order_mapping = sorted(list(all_mapping_keys))
    title_list = order_first + order_link + order_labels + order_dr + order_mapping
    csv_output = [title_list]
    for entry in results:
        record = [entry[i] for i in order_first]
        record += ['https://github.com/UKNCSP/CDDS-CMIP7-mappings/issues/{}'.format(entry['issue_number'])]
        record += [' '.join(entry['labels'])]
        record += [entry['Data Request information'].get(i, "") for i in order_dr]
        record += [entry['Mapping information'].get(i, "") for i in order_mapping]
        csv_output.append(record)

    with open(os.path.join(output_dir, 'mappings.csv'), 'w') as fh:
        writer = csv.writer(fh, dialect='excel')
        for row in csv_output:
            writer.writerow(row)

    # prepare stash csv
    stash_headings = [
        'Model',
        'Branded variable name',
        'Frequency',
        'STASH',
        'Section',
        'Item',
        'time_profile',
        'domain_profile',
        'usage_profile',
    ]
    stash_csv = [stash_headings]
    for entry in results:
        stash_data = entry["STASH entries"] # (relevant for UM only)"]
        if not stash_data:
            continue
        for i in stash_data:
            line = [
                i['model'],
                entry['Data Request information']['Branded variable name'],
                entry['Data Request information']['Frequency'],
                i['STASH'],
                ]
            line += i['stash_number'].split(',')
            line += [i[j] for j in stash_headings[-3:]]
            stash_csv.append(line)
     
    with open(os.path.join(output_dir, 'stash.csv'), 'w') as fh:
        writer = csv.writer(fh, dialect='excel')
        for row in stash_csv:
            writer.writerow(row)  
        


