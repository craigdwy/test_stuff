#!/usr/bin/env python


""" Test script to query multiple machines using a queue. Found this to perform better than multiprocess"""

# python modules
import getpass
import os
import queue
import re
import threading

# 3rd Party
import paramiko


DRIVER_PATTERN = re.compile(r"Driver Version: (\d+.\d+.\d+)")
DRIVER_VERSION = "460.73.01"


def check_driver_version(ssh_session):
    """
    Check driver version
    :param paramiko sshClient ssh_session: ssh object to run commands
    return: bool
    """
    cmd = 'nvidia-smi'
    stdin, stdout, stderr = ssh_session.exec_command(cmd)
    output = stdout.read()
    matches = re.findall(DRIVER_PATTERN, output.decode("utf-8"))
    return True if matches and matches[0] == DRIVER_VERSION else False


class Worker(threading.Thread):
    """Threaded ssh worker"""

    def __init__(self, n_queue, machine_stats, user, password, process_func):
        """
        Worker to process items in the queue
        :param queue.Queue n_queue: contains the items to process
        :param dict machine_stats: Contains the machine results
        :param str user: username
        :param str password: password
        """
        threading.Thread.__init__(self)
        self.queue = n_queue
        self.machine_stats = machine_stats
        self.user = user
        self.password = password
        self.machine_stats['good'] = []
        self.machine_stats['bad'] = []
        self.process_func = process_func

    def run(self):
        host = self.queue.get()

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(host, username=self.user, timeout=20, password=self.password)

            if self.process_func(ssh):
                self.machine_stats['good'].append(host)
            else:
                self.machine_stats['bad'].append(host)
        except Exception as error:
            print(error, '-', host)
            self.machine_stats['bad'].append(host)


def get_hosts():
    """
    Update this function to get a list of host to execute commands on
    """
    return ['localhost']


def main():
    user = os.getenv('USER')
    password = getpass.getpass()
    machine_queue = queue.Queue()
    machine_status = {}

    machine_list = get_hosts()
    for machine in machine_list:
        machine_queue.put(machine)

    # initiate threads to handle ssh + execution of commands
    for i in range(machine_queue.qsize()):
        thread = Worker(machine_queue, machine_status, user, password, check_driver_version)
        thread.setDaemon(True)
        thread.start()
    thread.join()

    for k, v in machine_status.items():
        print(k, ' '.join(v))


if __name__ == '__main__':
    main()
