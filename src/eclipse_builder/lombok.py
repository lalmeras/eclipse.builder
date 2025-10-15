import os.path
import shutil

from eclipse_builder import util


def install_lombok(cache_dir, eclipse_home, lombok_jar):
    """Install lombok in eclipse folder"""
    if lombok_jar:
        plugin = os.path.basename(lombok_jar)
        target = os.path.join(eclipse_home, plugin)
        print(f"Installing dropin plugin {plugin}")
        downloaded = util.download(cache_dir, lombok_jar)
        try:
            with open(target, 'wb') as target_f:
                shutil.copyfileobj(downloaded, target_f)
        finally:
            downloaded.close()