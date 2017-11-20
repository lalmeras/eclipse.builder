"""Utilities for Eclipse Builder"""
from __future__ import print_function

import datetime
import logging
import os.path
import shutil
import subprocess
import sys
import tempfile

import requests
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache

logger = logging.getLogger(__name__)

def download(workdir, url):
    """Download a file, using .cache inside workdir as an HTTP cache."""
    logging.debug(u"initializing requests and cache-control")
    session = CacheControl(requests.Session(),
                           cache=FileCache(os.path.join(workdir, '.cache')))
    req = session.get(url, stream=True)
    try:
        downloaded_file = tempfile.TemporaryFile()
        size = 0
        start = datetime.datetime.now()
        for chunk in req.iter_content(chunk_size=1024000):
            if chunk:
                sys.stdout.write('.')
                sys.stdout.flush()
                downloaded_file.write(chunk)
                size += len(chunk)
        # print newline
        print()
        downloaded_file.flush()
        logging.info(u"downloaded {} - {} o. in {} s.",
                     url, size,
                     (datetime.datetime.now() - start).total_seconds())
        logging.debug(u"reset file pointer - seek(0)")
        downloaded_file.seek(0)
        return downloaded_file
    except Exception as exc:
        logging.debug(u"error on download, closing and deleting file")
        downloaded_file.close()
        raise exc


def extract(tarobj, target):
    """Extract a *tarobj* tarfile object"""
    print(target)
    for member in tarobj.getmembers():
        if '..' in member.name:
            print('{} ignored during extraction'.format(member.name))
            continue
        if member.name.startswith('/'):
            print('{} ignored during extraction'.format(member.name))
            continue
        if '/' in member.name:
            splitted = os.path.join(*member.name.split('/')[1:])
            target_item = os.path.join(target, splitted)
            if not os.path.exists(target_item):
                if member.isreg():
                    with open(target_item, 'w') as target_file:
                        shutil.copyfileobj(tarobj.extractfile(member),
                                           target_file)
                        os.chmod(target_file.name, member.mode)
                elif member.isdir():
                    os.mkdir(target_item)
                    os.chmod(target_item, member.mode)
                else:
                    print('{} ignored during extraction'.format(member.name))


def archive(eclipse_home, basename, archive_file):
    """Compress en archive target"""
    args = [
        'tar', '-czf', archive_file,
        '--transform', 's@^@{}/@'.format(basename),
        '-C', eclipse_home, '.'
    ]
    subprocess.check_call(args)
