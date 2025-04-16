#! /bin/env python
"""Plugin installed"""

import os.path
import shutil

from eclipse_builder import util


def install_plugins(cache_dir, eclipse_home, dropins):
    """Install plugins in plugins folder of an Eclipse instance"""
    for url in dropins:
        plugin = os.path.basename(url)
        target = os.path.join(eclipse_home, "plugins", plugin)
        print(f"Installing plugins {plugin}")
        downloaded = util.download(cache_dir, url)
        try:
            with open(target, 'wb') as target_f:
                shutil.copyfileobj(downloaded, target_f)
        finally:
            downloaded.close()
