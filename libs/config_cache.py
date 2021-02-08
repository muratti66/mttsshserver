from typing import Any
from configobj import ConfigObj

CONF_PATH = "config.cfg"


class ConfigCache:
    """
    Config Parser Class
    """

    def __init__(self, config_path=None):
        """
        First initialization
        """
        global CONF_PATH
        if config_path is None:
            c_path = CONF_PATH
        else:
            c_path = config_path
        self.__config_db = ConfigObj(c_path)
        self.__return_map = dict()
        for key, value in self.__config_db.iteritems():
            self.__return_map.update({key: value})

    def get_value(self, in_section=str(), in_key=str()) -> Any:
        """
        Return value from loaded config parse object
        :type in_section: section key str
        :type in_key: key str
        :return: str
        """
        if in_section in self.__return_map.keys():
            if in_key in self.__return_map.get(in_section).keys():
                return self.__return_map.get(in_section).get(in_key)

        return None
