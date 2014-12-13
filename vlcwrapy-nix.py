#!/usr/bin/env python
import subprocess
import sys
import appindicator
import gtk
import os
import natsort
import gobject
import time

def display(report):
    os.system('zenity --info --text="{}"'.format(report))

class Vlc:
    def __init__(self,filename):        
        self.now_playing=filename
        self.process=None
        self.play()

    def restart(self,filename):
        self.kill()
        self.now_playing=filename
        self.play()

    def play(self):
        if not self.is_alive():
            self.process=subprocess.Popen(['vlc',self.now_playing])

    def kill(self):
        p, self.process = self.process, None
        if p is not None and p.poll() is None:
            p.kill() 
            p.wait()

    def is_alive(self):
        if self.process is not None and self.process.poll() is  None:
            return True
        else:
            return False


def get_new_file(**kwargs):
    direction,current=kwargs['direction'],os.path.basename(kwargs['current'])
    supplist=['.mkv','.flv','.avi','.mpg','.wmv','.ogm','.mp4','.rmvb']
    files=natsort.natsorted([filename for filename in os.listdir('.') if os.path.splitext(filename)[-1].lower() in supplist])
    return os.path.realpath(files[(files.index(current)+direction)%len(files)])

def lookupIcon(icon_name):    
    icon_theme = gtk.icon_theme_get_default()               
    return icon_theme.lookup_icon(icon_name, 48, 0).get_filename()

class Indicator:
    def __init__(self,init_file,vlc):
        self.a = appindicator.Indicator('appmenu',lookupIcon('vlc'), appindicator.CATEGORY_APPLICATION_STATUS)
        self.a.set_status( appindicator.STATUS_ACTIVE )
        self.current=init_file
        self.build_menu()
        self.vlc=vlc
        gobject.timeout_add(10*1000, self.callback)
        self.last_alive=0

    
    def callback(self):
        if self.vlc.is_alive():
            self.last_alive=time.time()
        else:
            dead_since=time.time()-self.last_alive
            if dead_since>1:
                gtk.mainquit()
        return True


    def make_item(self,name,icon):
        item=gtk.ImageMenuItem(name)
        img=gtk.Image()
        img.set_from_file(lookupIcon(icon))
        item.set_image(img)
        item.show()
        return item

    def build_menu(self):
        menu=gtk.Menu()
        prev_file_item=self.make_item('Previous','gtk-media-next-rtl')
        prev_file_item.connect('activate',self.prev_next_handler,-1)
        menu.append(prev_file_item)
        next_file_item=self.make_item('Next','gtk-media-next-ltr')
        next_file_item.connect('activate',self.prev_next_handler,1)
        menu.append(next_file_item)
        reload_item=self.make_item('Resume','reload')
        menu.append(reload_item)
        self.a.set_menu(menu)

    def prev_next_handler(self,item,direction):
        f=get_new_file(direction=direction,current=self.current)
        self.vlc.restart(f)

def main():
    path=sys.argv[1]    
    vlc=Vlc(path)
    indicator=Indicator(path,vlc)
    gtk.main()


if __name__ == '__main__':
    main()

