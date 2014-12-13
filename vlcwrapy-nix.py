#!/usr/bin/env python
import subprocess, sys, os, time, psutil
import appindicator, gtk, gobject, notify2
import natsort
import pyxhook as hook
import atexit as at_exit
import pickle
# syspath = os.path.abspath((os.path.dirname(os.readlink(__file__))))
# if not syspath in sys.path:
#     sys.path.insert(1, syspath)
# del syspath

statefile=os.path.expanduser('~/.vlcwrapy-nix/vlcdatabase.p')
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
def fetch_watch_table():
    if os.path.exists(statefile):
        with open(statefile) as f:
            try:
                table=pickle.load(f)
            except:
                table={}
    else:
        if not os.path.exists(os.path.dirname(statefile)):
            os.makedirs(os.path.dirname(statefile))
        table={}
    return table

def get_new_file(**kwargs):
    direction,current=kwargs['direction'],os.path.basename(kwargs['current'])
    supplist=['.mkv','.flv','.avi','.mpg','.wmv','.ogm','.mp4','.rmvb']
    files=natsort.natsorted([filename for filename in os.listdir('.') 
                    if os.path.splitext(filename)[-1].lower() in supplist])
    if direction==2:
        table=fetch_watch_table()
        state=table.get(os.getcwd(),None)
        if state:
            newfile=os.path.realpath(state)
        else :
            return False
    else:
        newfile= os.path.realpath(files[(files.index(current)+direction)%len(files)])
    return newfile

def lookupIcon(icon_name):    
    icon_theme = gtk.icon_theme_get_default()               
    return icon_theme.lookup_icon(icon_name, 48, 0).get_filename()

class Indicator:
    def __init__(self,path):        
        self.a = appindicator.Indicator('appmenu',lookupIcon('vlc'), appindicator.CATEGORY_APPLICATION_STATUS)
        self.a.set_status( appindicator.STATUS_ACTIVE )
        self.vlc=Vlc(path) 
        self.build_menu()
        gobject.timeout_add(10*1000, self.quitCallback)
        at_exit.register(self.save_state)        
        self.last_alive=0
   
    def quitCallback(self):
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
        prev_file_item.connect('activate',self.menuHandler,-1)
        menu.append(prev_file_item)
        next_file_item=self.make_item('Next','gtk-media-next-ltr')
        next_file_item.connect('activate',self.menuHandler,1)
        menu.append(next_file_item)
        reload_item=self.make_item('Resume','reload')
        menu.append(reload_item)
        self.a.set_menu(menu)

    def menuHandler(self,item,direction):
        f=get_new_file(direction=direction,current=self.vlc.now_playing)
        if f:
            self.vlc.restart(f)    


    def save_state(self):
        table=fetch_watch_table()
        table[os.getcwd()]=self.vlc.now_playing
        with open(statefile,'w') as f:
            pickle.dump(table,f)

def seek_and_destroy(to_kill):
    for process in psutil.get_process_list():
        # print process
        if process.name()==to_kill:
            process.kill()

class Message:
    def __init__(self,title):
        self.title=title
        notify2.init("title")
        self.notice = notify2.Notification(title, 'automation-indicator active')
        # self.notice.show()
    def display_error(self,message):
        self.notice.update(self.title,message)
        return self.notice.show()
notify=Message('vlcwrapy-nix')

class Hook:
    def __init__(self,indicator):
        self.ind=indicator
        self.hm=hook.HookManager()
        self.hm.HookKeyboard()
        self.hm.KeyDown=self.kbeventhandler
        self.hm.start()
    def kbeventhandler(self,event):    
        # print event
        if event.Key=='Home' and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None,-1)
            # print 'home'
        if event.Key=='End' and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None,1)
            # print 'end'
        if event.Key=='F2'  and 'vlc' in event.WindowProcName.lower():
            self.ind.menuHandler(None,2)
            # print 'F2'
        # print 'event detected'

    def kill(self):
        time.sleep(2)
        self.hm.cancel()

def main():    
    gobject.threads_init()
    path=sys.argv[1]
    seek_and_destroy('vlc')       
    indicator=Indicator(path)
    KBhook=Hook(indicator)
    gtk.main()
    KBhook.kill()

if __name__ == '__main__':
    main()
