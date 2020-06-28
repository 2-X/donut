import re
import platform
import requests
import time
import os
import subprocess
import zipfile

from utils.download_utils import download_ngrok
from utils.filepath_utils import fix_filepath


class Ngrok:
    """ ngrok tunnel """
    public_url = None
    ngrok_filepath = None
    system_version = platform.system()

    def init(self):
        # download ngrok if it isn't already downloaded
        self.download()

        # kill previous ngrok instances
        self.quit()

        # wait a second so it doesn't kill the ngrok we spawn down below
        time.sleep(2)

        # spawn a new process in the background
        if self.system_version == "Linux":
            os.system(f'{self.ngrok_filepath} http 5000 > /dev/null &')
        elif self.system_version == "Darwin":
            # TODO figure out if this works
            os.system(f'{self.ngrok_filepath} http 5000 > /dev/null &')
        elif self.system_version == "Windows":
            os.system(f'start {self.ngrok_filepath} http 5000')

        # give it some time to spawn the process
        time.sleep(6)

        # record properties
        self.public_url = self._get_public_url()

    def download(self):
        # download ngrok if it isn't already downloaded
        self.ngrok_filepath = fix_filepath(download_ngrok())

    def quit(self):
        if self.system_version == "Linux":
            subprocess.Popen(["killall", "-9", "ngrok"])
        elif self.system_version == "Darwin":
            subprocess.Popen(["killall", "-9", "ngrok"])
        elif self.system_version == "Windows":
            subprocess.Popen(["taskkill", "/IM", "ngrok.exe", "/F"])
        else:
            raise Exception(f"Invalid operating system for running ngrok: {self.system_version}!")

    def _get_public_url(self):
        if (self.public_url):
            return self.public_url
        return requests.get("http://127.0.0.1:4040/api/tunnels").json().get("tunnels", [{}])[0].get("public_url").replace('http://', 'https://')
