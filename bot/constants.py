import toml
from pathlib import Path
import logging
import collections

log = logging.getLogger(__name__)

if Path("config.toml").exists():
    log.info("Loading config found at config.toml")
    with open("config.toml") as f:
        data = toml.load(f)
    log.debug("Loaded config data %s" % data)
else:
    log.info("config.toml not found, using default config")


class ConfigMeta(type):
    """
    Metaclass to allow accessing config data using dot notation, e.g. constants.Guild.token_file

    Supports arbitrary nesting of tables.
    """

    location = None

    def __getattr__(cls, name):
        name = name.lower()

        if cls.location is None:
            assert False

        try:
            path = collections.deque(cls.location.split("."))
            outer = data
            while path:
                n = path.popleft()
                if n:
                    outer = outer[n]
        except KeyError:
            log.error("Invalid location: %s", cls.location)
        else:
            try:
                return outer[name]
            except KeyError:
                log.error("Config value %s not found", name)


class Bot(metaclass=ConfigMeta):
    location = "bot"

    prefix: str
    token_file: str


class Guild(metaclass=ConfigMeta):
    location = "guild"

    teachers: list[int]
    student_channels: list[str]

class Snekbox(metaclass=ConfigMeta):
    location=""

    snekbox_url: str

