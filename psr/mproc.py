#!/usr/bin/env python
# -*- coding: utf-8 -*-
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                               #
#   software  : Kirmah <http://kirmah.sourceforge.net/>                         #
#   version   : 2.1                                                             #
#   date      : 2013                                                            #
#   licence   : GPLv3.0   <http://www.gnu.org/licenses/>                        #
#   author    : a-Sansara <http://www.a-sansara.net/>                           #
#   copyright : pluie.org <http://www.pluie.org/>                               #
#                                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#   This file is part of Kirmah.
#
#   Kirmah is free software (free as in speech) : you can redistribute it 
#   and/or modify it under the terms of the GNU General Public License as 
#   published by the Free Software Foundation, either version 3 of the License, 
#   or (at your option) any later version.
#
#   Kirmah is distributed in the hope that it will be useful, but WITHOUT 
#   ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or 
#   FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for 
#   more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Kirmah.  If not, see <http://www.gnu.org/licenses/>.


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module mproc ~~

from gi.repository.GObject   import timeout_add
from multiprocessing         import Process, Lock, Queue

from psr.decorate            import log
from psr.sys                 import Sys

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Ctrl ~~

class Ctrl:
    """"""
    @log
    def __init__(self, nproc, npqueue_bind=None, task=None, *args, **kwargs ):
        """"""
        self.plist    = []
        self.queue    = Queue()
        self.npqueue  = Queue()
        self.nproc    = nproc
        self.done     = False
        self.npq_bind = npqueue_bind
        if task is not None :
            self.bind_task(task, *args, **kwargs)

    def bind_task(self, task, *args, **kwargs):
        """"""
        if len(self.plist) > 0 :
            del self.plist
            self.plist = []
            del self.queue
            self.queue   = Queue()
            del self.npqueue
            self.npqueue = Queue()
        def mptask(npqueue, mproc_pid, mproc_queue, *args, **kwargs):
            def wrapped(*args, **kwargs):
                """Only queue need result"""
                def orgtask(*args, **kwargs):
                    Sys.g.MAIN_PROC  = None
                    Sys.g.NPQUEUE    = npqueue
                    return task(*args, **kwargs)
                mproc_queue.put_nowait([mproc_pid, orgtask(*args, **kwargs)])
            return wrapped(*args, **kwargs)

        for i in range(self.nproc):
            self.plist.append(Process(target=mptask, args=tuple([self.npqueue,i,self.queue,i])+tuple(args), kwargs=kwargs))
    
    @log
    def start(self, timeout=100, delay=None, maincb=None, childcb=None):
        """"""
        if childcb is not None : self.on_child_end = childcb
        if maincb is not None  : self.on_end = maincb
        if delay is None :
            self.launch(timeout)
        else :
            timeout_add(delay, self.launch, timeout)

    #~ @log        
    def launch(self, timeout):
        """"""
        for p in self.plist:p.start()
        self.list_process()
        self.tid = timeout_add(timeout, self.check)
        return False
        
    #~ @log        
    def list_process(self):
        """"""
        if Sys.g.DEBUG : 
            Sys.pcontent('current pid :'+str(Sys.getpid()))
            Sys.pcontent('childs pid :')
            for p in self.plist:
                Sys.pcontent(str(p.pid))
    
    #~ @log
    def end_process(self):
        """"""        
        if not self.queue.empty():
            d = self.queue.get_nowait()
            if d is not None :
                self.on_child_end(d[0], d[1])
                p = self.plist[d[0]]
                if p.is_alive(): p.join()

    #~ @log
    def on_child_end(self, pid, data):
        """"""

    #~ @log
    def end_task(self):
        """"""
        self.queue.close()
        self.queue.join_thread()
        self.done = True
        self.on_end()

    #~ @log
    def on_end(self):
        """"""
        print(self)
        print('all child process terminated')

    #~ @log
    def check(self):
        """"""
        leave = True
        # child process log queue
        if self.npq_bind is not None :
            while not self.npqueue.empty():
                d = self.npqueue.get_nowait()
                if d is not None: self.npq_bind(d)
        # ctrl queue
        if not self.queue.empty():
            self.end_process()
            for p in self.plist: leave = leave and not p.is_alive()
            if leave :
                while not self.queue.empty():
                    self.end_process()
                self.end_task()                
        else : leave = False
        return not leave


