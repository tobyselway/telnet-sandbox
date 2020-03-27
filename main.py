import os
import re
import signal
import socket
import sys
import threading
import multiprocessing
from multiprocessing import Queue
from pydoc import locate

PLUGIN_TIMEOUT = 5


def plugin_loader(plugin, q, args):
    class_name = ''.join(word.title() for word in plugin.split('_'))
    try:
        klass = locate('plugins.' + plugin + '.' + class_name)
        p = klass(q, args)
        p.run()
    except (KeyError, TypeError):
        print("[System] cannot find the " + class_name + "(Plugin) class in the " + plugin + ".py file")
    except:
        print("[System] Error loading plugin " + class_name)


def run_plugin(wrapper, plugin, q, in_str):
    args = in_str.split()
    if not args:
        args = [""]
    p = multiprocessing.Process(target=wrapper, args=(plugin, q, args))
    p.start()
    p.join(PLUGIN_TIMEOUT)
    if p.is_alive():
        p.terminate()
        print("[System] " + plugin.__name__ + " timed out")


class Pipeline:

    @staticmethod
    def run(in_str, q):
        plugins = os.listdir("plugins")
        for plugin in plugins:
            if plugin.endswith(".py") and plugin != "__pycache__.py":
                plugin = plugin.replace(".py", "")
                run_plugin(plugin_loader, plugin, q, in_str)


class Server(threading.Thread):
    def __init__(self, sock, addr):
        threading.Thread.__init__(self)
        self.socket = sock
        self.address = addr

    def run(self):
        lock.acquire()
        clients.append(self)
        lock.release()
        out_buffer = "> "
        out_data = out_buffer.encode()
        self.socket.send(out_data)
        print('%s:%s connected' % self.address)
        while True:
            in_data = self.socket.recv(1024)
            if not in_data:
                break

            try:
                in_buffer = in_data.decode('utf-8').rstrip()
                if in_buffer == "exit" or in_buffer == "quit":
                    break

                out_buffer = ""

                if in_buffer != "":
                    q = Queue()
                    Pipeline.run(in_buffer, q)
                    if not q.empty():
                        while not q.empty():
                            out_buffer += q.get() + "\n"
                    else:
                        out_buffer += "Command Not Found. Consider writing a plugin to implement it.\n"

                out_buffer += "> "
            except:
                out_buffer = "> "

            out_data = out_buffer.encode()

            self.socket.send(out_data)
        self.socket.close()
        print('%s:%s disconnected' % self.address)
        lock.acquire()
        clients.remove(self)
        lock.release()


running = True


def signal_handler(sig, frame):
    print('Stopping server')
    global running
    running = False
    s.detach()
    s.close()
    sys.exit(0)


HOST = ''
PORT = 23

if len(sys.argv) > 1:
    HOST = sys.argv[1]
    if len(sys.argv) > 2:
        PORT = int(sys.argv[2])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(4)
clients = []  # list of clients connected
lock = threading.Lock()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("Server running on " + ("127.0.0.1" if HOST == "" else HOST) + ":" + str(PORT))

    while running:  # wait for socket to connect
        try:
            # send socket to server and start monitoring
            (sock, addr) = s.accept()
            Server(sock, addr).start()
        except socket.timeout as e:
            pass

    sys.exit(0)
