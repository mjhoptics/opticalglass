#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Support for downloading the RefractiveIndex.INFO database from GitHub.

fork of https://github.com/toftul/refractiveindex/refractiveindex/refractiveindex.py under the following license:

MIT License

Copyright (c) 2023 Ivan Toftul

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
----------------------------------------------------------------------------
Modifications include:
- use logging for informative output
- minimal comments
"""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Latest commit as of 2026-02-17
# https://github.com/polyanskiy/refractiveindex.info-database/commits/master/
_DATABASE_SHA = "a66ef8805cdb200973fc7ae9181587e1d89d14eb"

_DEFAULT_DB_PATH = Path.home() / ".refractiveindex.info-database"


def download_database(db_path: Path, ssl_certificate_location: str|None=None):
    """Download the RefractiveIndex.INFO database from GitHub and extract it to db_path."""
    import shutil
    import ssl
    import tempfile
    import urllib.request
    import zipfile

    url = f"https://github.com/polyanskiy/refractiveindex.info-database/archive/{_DATABASE_SHA}.zip"

    if ssl_certificate_location is not None:
        if ssl_certificate_location == "":
            ssl._create_default_https_context = ssl._create_unverified_context
        else:
            if (not ssl_certificate_location.endswith(".pem") or 
                not Path(ssl_certificate_location).is_file()):
                raise ValueError(
                    f"Does not appear to be an existing .pem certificate file: {ssl_certificate_location}"
                )
            ssl._create_default_https_context = ssl.create_default_context(cafile=ssl_certificate_location)

    with tempfile.TemporaryDirectory() as tempdir:
        zip_path = Path(tempdir) / "db.zip"
        
        logger.info("downloading refractiveindex.info database...")
        urllib.request.urlretrieve(url, zip_path)
        
        logger.info("extracting...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tempdir)

        if db_path.is_dir():
            logger.info("removing old database...")
            shutil.rmtree(db_path)

        extracted = (Path(tempdir) / 
                     f"refractiveindex.info-database-{_DATABASE_SHA}" / 
                     "database")
        shutil.move(str(extracted), str(db_path))

        logger.info("done")


def ensure_database(db_path: Path, auto_download: bool, 
                    update_database: bool, 
                    ssl_certificate_location: str|None):
    """Ensure that the RefractiveIndex.INFO database exists at db_path, downloading if necessary and allowed."""
    if not db_path.exists() and auto_download or update_database:
        download_database(db_path, ssl_certificate_location)
    logger.info("rii DB ensured")
    return db_path
