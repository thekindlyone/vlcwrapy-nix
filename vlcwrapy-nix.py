#!/usr/bin/env python
import subprocess
import sys
import os
import time
import psutil
import appindicator
import gtk
import gobject
import notify2
import natsort
import pyxhook as hook
import atexit as at_exit
import pickle
import argparse

statefile = os.path.expanduser('~/.vlcwrapy-nix/vlcdatabase.p')
show_notifications = True


class Vlc:

    def __init__(self, filename):
        self.now_playing = filename
        self.process = None
        self.play()

    def restart(self, filename):
        self.kill()
        self.now_playing = filename
        self.play()

    def play(self):
        if not self.is_alive():
            self.process = subprocess.Popen(['vlc', self.now_playing])

    def kill(self):
        p, self.process = self.process, None
        if p is not None and p.poll() is None:
            p.kill()
            p.wait()

    def is_alive(self):
        if self.process is not None and self.process.poll() is None:
            return True
        else:
            return False


def fetch_watch_table():
    if os.path.exists(statefile):
        with open(statefile) as f:
            try:
                table = pickle.load(f)
            except:
                table = {}
    else:
        if not os.path.exists(os.path.dirname(statefile)):
            os.makedirs(os.path.dirname(statefile))
        table = {}
    return table


def get_new_file(**kwargs):
    direction, current = kwargs[
        'direction'], os.path.basename(kwargs['current'])
    supplist = ['.mkv', '.flv', '.avi', '.mpg',
                '.wmv', '.ogm', '.mp4', '.rmvb', '.m4v']
    files = natsort.natsorted([filename for filename in os.listdir('.')
                               if os.path.splitext(filename)[-1].lower() in supplist])
    if direction == 2:
        table = fetch_watch_table()
        state = table.get(os.getcwd(), None)
        if state:
            newfile = os.path.realpath(state)
        else:
            return False
    else:
        newfile = os.path.realpath(
            files[(files.index(current) + direction) % len(files)])
    return newfile


def lookupIcon(icon_name):
    icon_theme = gtk.icon_theme_get_default()
    return icon_theme.lookup_icon(icon_name, 48, 0).get_filename()


class Indicator:

    def __init__(self, path):
        self.a = appindicator.Indicator(
            'appmenu', lookupIcon('vlc'), appindicator.CATEGORY_APPLICATION_STATUS)
        self.a.set_status(appindicator.STATUS_ACTIVE)
        self.vlc = Vlc(path)
        self.build_menu()
        gobject.timeout_add(5 * 1000, self.quitCallback)
        at_exit.register(self.save_state)
        self.last_alive = 0

    def quitCallback(self):
        if self.vlc.is_alive():
            self.last_alive = time.time()
        else:
            dead_since = time.time() - self.last_alive
            if dead_since > 2:
                gtk.mainquit()
        return True

    def make_item(self, name, icon):
        item = gtk.ImageMenuItem(name)
        img = gtk.Image()
        img.set_from_file(lookupIcon(icon))
        item.set_image(img)
        item.show()
        return item

    def build_menu(self):
        menu = gtk.Menu()
        prev_file_item = self.make_item('Previous', 'gtk-media-next-rtl')
        prev_file_item.connect('activate', self.menuHandler, -1)
        menu.append(prev_file_item)
        next_file_item = self.make_item('Next', 'gtk-media-next-ltr')
        next_file_item.connect('activate', self.menuHandler, 1)
        menu.append(next_file_item)
        reload_item = self.make_item('Resume', 'reload')
        menu.append(reload_item)
        self.a.set_menu(menu)

    def menuHandler(self, item, direction):
        f = get_new_file(direction=direction, current=self.vlc.now_playing)
        if f:
            self.vlc.restart(f)

    def save_state(self):
        table = fetch_watch_table()
        table[os.getcwd()] = self.vlc.now_playing
        table['lastplayed'] = os.path.join(os.getcwd(), self.vlc.now_playing)
        with open(statefile, 'w') as f:
            pickle.dump(table, f)


def seek_and_destroy(to_kill):
    for process in psutil.get_process_list():
        # print process
        if process.name() == to_kill:
            process.kill()


class Message:

    def __init__(self, title):
        self.title = title
        notify2.init("title")
        self.notice = notify2.Notification(
            title, 'automation-indicator active')
        # self.notice.show()

    def display(self, message, icon=None):
        self.notice.update(self.title, message, icon=icon)
        self.notice.timeout = 100
        if show_notifications:
            self.notice.show()
notify = Message('vlcwrapy-nix')


class Hook:

    def __init__(self, indicator):
        self.ind = indicator
        self.hm = hook.HookManager()
        self.hm.HookKeyboard()
        self.hm.KeyDown = self.kbeventhandler
        self.hm.start()

    def kbeventhandler(self, event):
        # print event
        if event.Key == 'Home' and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None, -1)
            notify.display('[Home] Previous file', 'gtk-media-next-rtl')
            # print 'home'
        if event.Key == 'End' and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None, 1)
            notify.display('[End] Next File', 'gtk-media-next-ltr')
            # print 'end'
        if event.Key == 'F2' and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None, 2)
            notify.display(
                '[F2] Loading last played in current directory', 'reload')
            # print 'F2'
        # print 'event detected'

    def kill(self):
        time.sleep(2)
        self.hm.cancel()

from datetime import datetime
logfile=os.path.expanduser('~/.vlcwrapy-nix/vlcwrapy-nix.log')
def log(logline):
    with open(logfile,'a') as f:
        f.write(logline+'\n')




def main():
    gobject.threads_init()
    log('\n\n\nStarted '+str(datetime.now()))
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runfromfile", help="run vlcwrapy-nix from file", nargs='?')
    parser.add_argument("location", help="file to open", nargs='?')
    args = parser.parse_args()
    log('args={}\nargs={}'.format(str(sys.argv),str(args)))
    # if args.runfromfile:      



    if not args.location:
        lastwatched = fetch_watch_table().get('lastplayed', False)
        if lastwatched:
            filedir, path = os.path.split(lastwatched)
            os.chdir(filedir)
        else:
            notify.display('Run vlcwrapy-nix from a video file.', 'error')
            sys.exit()
    else:
        if args.runfromfile:
            filedir, path = os.path.split(args.location)
            os.chdir(filedir)
        else:
            path = args.location
    log('filename received={}\n cwd={}'.format(path,os.getcwd()))
    notify.display('filename received={}\n cwd={}'.format(path,os.getcwd()),'vlc')
    seek_and_destroy('vlc')
    indicator = Indicator(path)
    KBhook = Hook(indicator)
    gtk.main()
    KBhook.kill()

if __name__ == '__main__':
    main()


'''
arguments =['/home/thekindlyone/projects/nautilus-test.py', '/media/thekindlyone/storage/anime/Guilty Crown/[Commie] Guilty Crown - 10 [6094511C].mkv']
cwd=/home/thekindlyone
'''
