#!/usr/bin/env python
# # -*- coding: utf-8 -*-
#
# """ ==================================================================
# Script Name: solstice_tools_deployer_utils.py
# by Tomás Poveda
# ______________________________________________________________________
# Utilities functions for deployer
# ______________________________________________________________________
# ==================================================================="""

import re
import urllib2
import tempfile
import os
import json

numbers = re.compile('\d+')

def sLog(text):
    return '| Solstice Tools | => {}'.format(text)

def downloadFile(filename, destination):
    try:
        dstFolder = os.path.dirname(destination)
        if not os.path.exists(dstFolder):
            os.makedirs(dstFolder)
        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}
        req = urllib2.Request(filename, headers=hdr)
        data = urllib2.urlopen(req)
        # with open(destination, 'ab') as dstFile:
        #     dstFile.write(data.read())
        chunk_read(response=data, destination=destination, report_hook=chunk_report)
    except Exception as e:
        raise e
    if os.path.exists(destination):
        return True
    else:
        return False


def chunk_report(bytes_so_far, chunk_size, total_size):
    percent = float(bytes_so_far) / total_size
    percent = round(percent*100, 2)
    if bytes_so_far >= total_size:
        print('\n')


def chunk_read(response, destination, chunk_size=8192, report_hook=None):

    with open(destination, 'ab') as dst_file:
        total_size = response.info().getheader('Content-Length').strip()
        total_size = int(total_size)
        bytes_so_far = 0
        while 1:
            chunk = response.read(chunk_size)
            dst_file.write(chunk)
            bytes_so_far += len(chunk)
            if not chunk:
                break
            if report_hook:
                report_hook(bytes_so_far, chunk_size, total_size)
    dst_file.close()
    return bytes_so_far


def getVersion(s):
    """ look for the last sequence of number(s) in a string and increment """
    if numbers.findall(s):
        lastoccr_sre = list(numbers.finditer(s))[-1]
        lastoccr = lastoccr_sre.group()
        return lastoccr
    return None


def get_last_solstice_tools_version(as_int=False):

    temp_path = tempfile.mkdtemp()
    repo_url = 'http://cgart3d.com/solstice_tools/'
    setup_file = '{}setup.json'.format(repo_url)
    setup_path = os.path.join(temp_path, 'setup.json')
    if not downloadFile(setup_file, setup_path):
        raise Exception(sLog(
            'ERROR: setup.json is not accessible. It was nos possible to install solstice_tools. Check your internet connection and retry'))
    with open(setup_path, 'r') as fl:
        setup_info = json.loads(fl.read())
    last_version = setup_info.get('lastVersion')
    if not last_version:
        raise Exception(sLog('ERROR: Last version uploaded is not available. Try again later!'))

    if as_int:
        return int(getVersion(last_version))
    else:
        return last_version