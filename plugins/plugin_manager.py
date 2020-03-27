import os
import re
import requests
from plugin import Plugin

LOCKED_PLUGINS = ["plugin_manager", "clear"]


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


class PluginManager(Plugin):

    def run(self):

        if self.args[0] == "p":

            if self.args[1] == "list":
                plugins = os.listdir("plugins")
                p_list = ""
                p_count = 0
                for plugin in plugins:
                    if plugin.endswith(".py") and plugin != "":
                        plugin = plugin.replace(".py", "")
                        p_list += "\n"
                        if LOCKED_PLUGINS.__contains__(plugin):
                            p_list += " * "
                        else:
                            p_list += " - "
                        p_list += plugin
                        p_count += 1
                self.print("total " + str(p_count) + p_list)

            elif self.args[1] == "add":
                if len(self.args) < 3:
                    self.print("Plugin Downloader: missing parameter name")
                else:
                    name = camel_to_snake(self.args[2])
                    if LOCKED_PLUGINS.__contains__(name):
                        self.print("Plugin Downloader: '" + name + "' is a locked plugin.")
                    else:
                        if len(self.args) < 4:
                            self.print("Plugin Downloader: missing parameter url")
                        else:
                            url = self.args[3]

                            r = requests.get(url)

                            with open('plugins/' + name + '.py', 'wb') as f:
                                f.write(r.content)
                            self.print("Successfully imported '" + name + "'.")

            elif self.args[1] == "delete":
                if len(self.args) < 3:
                    self.print("Plugin Downloader: missing parameter name")
                else:
                    name = camel_to_snake(self.args[2])
                    if LOCKED_PLUGINS.__contains__(name):
                        self.print("Plugin Downloader: '" + name + "' is a locked plugin.")
                    else:
                        try:
                            os.remove("plugins/" + name + ".py")
                            self.print("Plugin Downloader: successfully deleted '" + name + "'.")
                        except:
                            self.print("Plugin Downloader: cannot find '" + name + "'.")

            else:
                self.print("Plugin Downloader: invalid argument '" + self.args[1] + "'")
