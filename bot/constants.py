import toml
from pathlib import Path
import logging
import collections

log = logging.getLogger(__name__)

if Path("config.toml").exists():
    log.info("Loading config found at config.toml")
    with open("config.toml") as f:
        data = toml.load(f)
    print(data)
else:
    log.error("No config, exiting")
    exit(1)


class ConfigMeta(type):
    """
    Metaclass to allow accessing config data using dot notation, e.g. constants.Guild.BOT_TOKEN

    Supports arbitrary nesting of tables.
    """

    location = None

    def __getattr__(cls, name):
        name = name.lower()

        if cls.location is None:
            assert False

        location = collections.deque(cls.location.split("."))

        try:
            outer = data[location.popleft()]
            while location:
                outer = outer[location.popleft()]
        except KeyError:
            print(f"Invalid location: {cls.location}")
        else:
            try:
                return outer[name]
            except KeyError:
                print(f"Config value {name} not found")


class Bot(metaclass=ConfigMeta):
    location = "bot"
    prefix: str
    token_file: str


class Guild(metaclass=ConfigMeta):
    location = "guild"
    teachers: list[int]
