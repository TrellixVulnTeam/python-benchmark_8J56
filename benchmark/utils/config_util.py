"""
global configuration object. only support string for now

"""

import ConfigParser


def singleton(cls):
    instance = cls()
    instance.__call__ = lambda: instance
    return instance


@singleton
class Configuration():
    def __init__(self):
        self.groups = dict()

    def register_opt(self, key, value, group="DEFAULT"):
        group = self.groups.get(group)
        group.update({key: value})

    def register_group(self, group):
        self.groups.update({group: dict()})

    def get_opt(self, key, group="DEFAULT"):
        group = self.groups.get(group)
        return group.get(key)

    def get_int_opt(self, key, group="DEFAULT"):
        value = self.get_opt(key, group)
        return int(value)

    def parse_ini(self, path):
        parser = ConfigParser.ConfigParser()
        parser.read(path)

        for section in parser.sections():
            group_name = section
            self.register_group(group_name)
            kvs = parser.items(section)
            for kv in kvs:
                key = kv[0]
                value = kv[1]
                self.register_opt(key, value, group_name)


def get_config():
    return Configuration()



