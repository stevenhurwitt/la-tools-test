from __future__ import print_function
from glob import glob
import os

__all__ = [os.path.basename(f)[:-3] for f in glob(os.path.dirname(__file__)+"/*.py")]

# These global variables have to be here for the HTML notebook page to be able to set them through injection
# DO NOT MOVE THESE
notebook_dir = "unset"
notebook_name = "unset"
client_timezone = "unset"


def _create_path(path):
    notebook_path = notebook_dir[:notebook_dir.rfind("/")]
    return os.path.join(notebook_path, path)[notebook_path.index('namespace-'+(os.environ['EWX_NAMESPACE'].replace(".","_"))):]
