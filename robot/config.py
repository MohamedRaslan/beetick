"""Configuration for the Robot implementation.

`BEE_TICK_BASE_URL` is deployment configuration, so it comes from the
environment or `.env`. Everything below it is runner policy: the defaults live
here and are overridden per run with Robot's ``--variable``, which takes
priority over this file.
"""

import os as _os
from pathlib import Path as _Path
from urllib.parse import urlparse as _urlparse

from dotenv import load_dotenv as _load_dotenv


_ROBOT_ROOT = _Path(__file__).resolve().parent
_load_dotenv(_ROBOT_ROOT / ".env")

BEE_TICK_BASE_URL = _os.getenv(
    "BEE_TICK_BASE_URL",
    "https://btech.com/en",
).rstrip("/")

_parsed_base_url = _urlparse(BEE_TICK_BASE_URL)
if _parsed_base_url.scheme not in {"http", "https"} or not _parsed_base_url.netloc:
    raise ValueError("BEE_TICK_BASE_URL must be an absolute HTTP(S) URL")

BROWSER = "chromium"
HEADLESS = True
RECORD_VIDEO = False
VIDEO_WIDTH = 1280
VIDEO_HEIGHT = 720

# Ceilings, not delays: every wait ends as soon as its condition is met.
ACTION_TIMEOUT = "10s"
NAVIGATION_TIMEOUT = "30s"
NETWORK_TIMEOUT = "15s"
IMAGE_TIMEOUT = "10s"

EXPECTED_DELIVERY_LOCATION = "Cairo"
