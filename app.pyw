# import eel
#
# eel.init('ui', allowed_extensions=['.js', '.html'])
#
#
# @eel.expose
# def get_console_log():
#     print("jap ierdole")
#     return 'jd'
#
#
# @eel.expose
# def python_say(x):
#     print(x)
#
#
# @eel.expose
# def restart():
#     print("restart")
#
#
# eel.start('index.html', size=(300, 600), disable_cache=False)
import os
import signal
import psutil

from rune_changer import main

import pystray
from PIL import Image

from threading import Thread

PROCNAME = "python.exe"


def stop_all():
    icon.stop()
    for proc in psutil.process_iter():
        if proc.name() == PROCNAME:
            proc.kill()


menu = pystray.Menu(pystray.MenuItem('Start', main.start), pystray.MenuItem('Stop', main.stop), pystray.MenuItem('Quit', stop_all))


image = Image.open("ui/icon.ico")
icon = pystray.Icon("Rune changer", icon=image, title="Rune changer by style", menu=menu)


def setup(icon):
    icon.visible = True


if __name__ == '__main__':
    t1 = Thread(target=main.run)
    t1.start()
    icon.run(setup)
