#!/usr/bin/env python3

#############################################################################
##
##  This file is part of GAP, a system for computational discrete algebra.
##
##  Copyright of GAP belongs to its developers, whose names are too numerous
##  to list here. Please refer to the COPYRIGHT file for details.
##
##  SPDX-License-Identifier: GPL-2.0-or-later
##

"""
This script collects the job-status of each package from _reports/
and generates a main test-status.json
"""

from utils import error, warning

import sys
import os
import glob
import json
from datetime import datetime

################################################################################
# Arguments
num_args = len(sys.argv)

if num_args > 5:
    error('Unknown number of arguments')

repo = runID = hash = hash_short ='Unknown'

if num_args > 1: repo = sys.argv[1]
if num_args > 2: runID = sys.argv[2]
if num_args > 3: hash = sys.argv[3]
if num_args > 4: hash_short = sys.argv[4]

################################################################################
# Collect the job-status of each package from _reports/
FILES = []
for FILE in glob.glob('_reports/**/*.json', recursive=True):
    FILES.append(FILE)

FILES.sort()

PKG_STATUS = {}

for FILE in FILES:
    PKG_STATUS[os.path.splitext(os.path.basename(FILE))[0]] = json.load(open(FILE, 'r'))


################################################################################
# Generate main test-status.json

# General Information
REPORT = {}
REPORT['repo'] = repo
REPORT['workflow'] = repo+'/actions/runs/'+runID
REPORT['hash'] = hash
REPORT['hash_short'] = hash_short
REPORT['date'] = str(datetime.now())

# Package Information
for pkg, data in PKG_STATUS.items():
    with open(os.path.join('packages', pkg, 'meta.json'), 'r') as f:
        meta = json.load(f)
    data['version'] = meta['Version']
    data['archive_url'] = meta['ArchiveURL']
    data['archive_sha256'] = meta['ArchiveSHA256']

REPORT['pkgs'] = PKG_STATUS

# Summary Information
REPORT['total'] = 0
REPORT['success'] = 0
REPORT['failure'] = 0
REPORT['cancelled'] = 0

for pkg, data in PKG_STATUS.items():
    REPORT['total'] += 1
    status = data['status']
    if status == 'success':
        REPORT['success'] += 1
    elif status == 'failure':
        REPORT['failure'] += 1
    elif status == 'cancelled':
        REPORT['cancelled'] += 1
    else:
        warning('Unknown job status \"'+status+'\" for pkg \"'+pkg+'\"')

with open('test-status.json', 'w') as f:
    json.dump(REPORT, f, ensure_ascii=False, indent=2)