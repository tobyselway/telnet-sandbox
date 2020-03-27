from plugin import Plugin


class Clear(Plugin):

    def run(self):

        if self.args[0] == "clear":
            self.print("\u001B[2J")
