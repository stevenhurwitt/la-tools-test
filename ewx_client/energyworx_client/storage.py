# TODO[MT]: This file should be moved to energyworx-jgscm

from __future__ import absolute_import

import os
import sys
import pandas as pd
# the next line is needed to prevent an error during i18n initialisation
# otherwise it will throw a NameError: s
# see: https://github.com/jupyter/notebook/issues/2798
import notebook.transutils
from energyworx_jgscm import GoogleStorageContentManager
import logging
from . import _create_path


logger = logging.getLogger()


if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO


def read_csv(file_path, **kwargs):
    content, fmt = GoogleStorageContentManager(skip_syncing=True).read_file(_create_path(file_path))
    return pd.read_csv(StringIO(content), **kwargs)


def list_dir(file_path, type=None, filter=None):
    excluded_files = ['.DS_Store']
    files = []
    gsm = GoogleStorageContentManager(skip_syncing=True)
    exists, members = gsm.list_files(_create_path(file_path)[1:], filter)
    blobs, folders = members
    for blob in blobs:
        if gsm.should_list(gsm._get_blob_name(blob)) and gsm._get_blob_name(blob) not in excluded_files \
                and (type is None or type in str(gsm._get_blob_name(blob))) and (filter is None or filter in str(gsm._get_blob_name(blob))):
            files.append(str((gsm._get_blob_name(blob))))
    return files


def read_file(file_name):
    raw_content, fmt = GoogleStorageContentManager(skip_syncing=True).read_file(_create_path(file_name))
    content = raw_content.decode('base64')
    return StringIO(content)


def to_csv(df, path):
    return GoogleStorageContentManager(skip_syncing=True).save_file(_create_path(path), df.to_csv())


def to_file(file_name, contents, extension=".json", domain=None, key_content=None):
    return GoogleStorageContentManager(skip_syncing=True, domain=domain, key_content=key_content).save_file(_create_path(file_name+extension), contents, True)

