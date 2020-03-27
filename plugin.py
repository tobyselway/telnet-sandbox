import abc


class Plugin:
    __metaclass__ = abc.ABCMeta

    def __init__(self, q, args):
        self.q = q
        self.args = args

    def print(self, msg):
        self.q.put(msg)

    @abc.abstractmethod
    def run(self):
        """Implement your plugin code here"""
        return
