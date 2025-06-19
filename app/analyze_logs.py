#!/usr/bin/env python3
"""
Simple log analysis script that uses GenAI to enhance the analysis.
This will search log files for specific terms and analyze the results.
"""

import os
import re
import sys
import argparse
import json
import pandas as pd
from datetime import datetime
from collections import Counter, defaultdict
from agent_helper import enhance_solutions, is_ai_enhancement_enabled

# Define column mapping for structured CSV logs
COLUMN_MAP = {
    "timestamp": "Timestamp",
    "severity": "Level",
    "component": "Component",
    "message": "Message"
}

def find_log_files(directory, max_files=100):
    log_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(('.log', '.csv')):
                log_files.append(os.path.join(root, file))
            if len(log_files) >= max_files:
                break
    return log_files

def load_csv_logs(file_path):
    try:
        df = pd.read_csv(file_path)
        required_columns = [COLUMN_MAP[c] for c in ["timestamp", "severity", "component", "message"]]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV file missing required columns: {required_columns}")
        entries = []
        for _, row in df.iterrows():
            entries.append({
                "file": file_path,
                "line_number": None,
                "content": f"{row[COLUMN_MAP['timestamp']]} {row[COLUMN_MAP['severity']]} [{row[COLUMN_MAP['component']]}]: {row[COLUMN_MAP['message']]}"
            })
        return entries
    except Exception as e:
        print(f"Error loading CSV {file_path}: {e}")
        return []

def search_files(files, search_term):
    matches = []
    for file_path in files:
        if file_path.endswith(".csv"):
            matches.extend(load_csv_logs(file_path))
        else:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    for i, line in enumerate(f):
                        if search_term.lower() in line.lower():
                            matches.append({
                                'file': file_path,
                                'line_number': i + 1,
                                'content': line.strip()
                            })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    return matches

def parse_log_entry(line):
    log_entry = {'raw': line}
    timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})|((\d{1,2}/\d{1,2}/\d{4})[ T]\d{2}:\d{2})', line)
    if timestamp_match:
        log_entry['timestamp'] = timestamp_match.group(0)
    severity_match = re.search(r'\b(ERROR|INFO|WARNING|DEBUG|CRITICAL|WARN|FATAL)\b', line, re.IGNORECASE)
    if severity_match:
        log_entry['severity'] = severity_match.group(1).upper()
    else:
        log_entry['severity'] = "UNKNOWN"
    if severity_match:
        remainder = line.split(severity_match.group(0), 1)[-1].strip()
    else:
        remainder = line
    component_match = re.search(r'\[([^\]]+)\]', remainder)
    if component_match:
        log_entry['component'] = component_match.group(1)
        message = remainder.split(']:', 1)[-1].strip()
        log_entry['message'] = message
    else:
        log_entry['message'] = remainder
    return log_entry

def analyze_log_entries(entries):
    total_entries = len(entries)
    severities = Counter()
    components = Counter()
    errors_by_component = defaultdict(list)
    timestamps = []
    for entry in entries:
        parsed = parse_log_entry(entry['content'])
        severities[parsed.get('severity', 'UNKNOWN')] += 1
        if 'component' in parsed:
            components[parsed['component']] += 1
            if parsed.get('severity') in ['ERROR', 'CRITICAL', 'FATAL']:
                errors_by_component[parsed['component']].append(parsed.get('message', ''))
        if 'timestamp' in parsed:
            timestamps.append(parsed['timestamp'])
    time_pattern = None
    if timestamps:
        try:
            timestamps = sorted(timestamps)
            time_pattern = {
                'first_occurrence': timestamps[0],
                'last_occurrence': timestamps[-1],
                'total_occurrences': len(timestamps)
            }
        except Exception as e:
            print(f"Error analyzing timestamps: {e}")
    error_patterns = []
    for component, errors in errors_by_component.items():
        for error in errors:
            if error and len(error) > 10:
                pattern = re.sub(r'\b[a-f0-9\-]{8,}\b', '<ID>', error)
                pattern = re.sub(r'\d+', '<NUM>', pattern)
                error_patterns.append((component, pattern))
    common_patterns = Counter(error_patterns).most_common(10)
    return {
        'total_entries': total_entries,
        'severity_distribution': dict(severities),
        'components': dict(components),
        'time_pattern': time_pattern,
        'error_patterns': [{'component': comp, 'pattern': pat, 'count': count}
                           for (comp, pat), count in common_patterns]
    }

def suggest_solutions(analysis):
    solutions = []
    patterns = [item['pattern'].lower() for item in analysis.get('error_patterns', [])]
    if any(pat for pat in patterns if 'connect' in pat or 'timeout' in pat):
        solutions.append({
            'problem': 'Connection issues',
            'solution': 'Check network settings, server availability, and timeouts.'
        })
    if any(pat for pat in patterns if 'permission' in pat or 'denied' in pat):
        solutions.append({
            'problem': 'Permission issues',
            'solution': 'Check file and system permissions, user roles, and ACLs.'
        })
    if any(pat for pat in patterns if 'memory' in pat or 'cpu' in pat or 'disk' in pat):
        solutions.append({
            'problem': 'System resource limits',
            'solution': 'Monitor and upgrade resource usage: RAM, CPU, storage.'
        })
    if not solutions:
        solutions.append({
            'problem': 'Uncategorized errors',
            'solution': 'Check logs manually. Consider refining component configs.'
        })
    return solutions

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--logs', type=str, default='./data/logs')
    parser.add_argument('--term', type=str, default='error')
    parser.add_argument('--output', type=str)
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--disable-ai', action='store_true')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    if args.disable_ai:
        os.environ['DISABLE_AI_ENHANCEMENT'] = 'true'
    if args.debug:
        os.environ['DEBUG'] = '1'

    log_files = find_log_files(args.logs)
    matches = search_files(log_files, args.term)
    analysis = analyze_log_entries(matches)
    solutions = suggest_solutions(analysis)

    result = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'search_term': args.term,
            'log_directory': args.logs,
            'total_files': len(log_files),
            'matches': len(matches)
        },
        'matches': matches,
        'analysis': analysis,
        'solutions': solutions
    }

    if is_ai_enhancement_enabled():
        try:
            result = enhance_solutions(result)
            result['ai_enhancement_used'] = True
        except Exception as e:
            result['ai_enhancement_used'] = False
            result['ai_error'] = str(e)
    else:
        result['ai_enhancement_used'] = False

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Saved results to {args.output}")
    else:
        print(json.dumps(result, indent=2))

if __name__ == '__main__':
    main()