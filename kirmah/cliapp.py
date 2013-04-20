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
# ~~ package cliapp ~~

import  kirmah.conf     as conf
from    kirmah.crypt    import KirmahHeader, Kirmah, BadKeyException, represents_int, KeyGen
from    kirmah.kctrl    import KCtrl
from    psr.sys         import Sys
from    psr.io          import Io

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class CliApp ~~

class CliApp:
    
    def __init__(self, home, path, parser, a, o):
        """"""
        self.parser = parser
        self.a      = a
        self.o      = o
        self.home   = home
        self.stime  = Sys.datetime.now()        
        if not self.o.keyfile : 
            self.o.keyfile = self.home+'.kirmah'+Sys.sep+'.default.key'


    def onCommandKey(self):
        """"""
        if int(self.o.length) >= 128 and int(self.o.length) <= 4096 :
            self.parser.print_header()                        
            if not self.o.outputfile : self.o.outputfile = self.home+'.kirmah'+Sys.sep+'.default.key'
            kg   = KeyGen(int(self.o.length))
            done = True
            if Io.file_exists(self.o.outputfile) and not self.o.force :
            
                Sys.pwarn((('the key file ',(self.o.outputfile, Sys.Clz.fgb3), ' already exists !'),
                           'if you rewrite this file, all previous files encrypted with the corresponding key will be unrecoverable !'))                            
                
                done   = Sys.pask('Are you sure to rewrite this file')
                self.stime  = Sys.datetime.now()                
            if done :
                Io.set_data(self.o.outputfile, kg.key)
            Sys.pstep('Generate key file', self.stime, done)

            if done : 
                Sys.print(' '*5+Sys.realpath(self.o.outputfile), Sys.Clz.fgB1, True)
            
        else :
            self.parser.error_cmd((('invalid option ',('-l, --length', Sys.Clz.fgb3), ' value (', ('128',Sys.Clz.fgb3),' to ', ('4096',Sys.Clz.fgb3),')'),))
    

    def onCommandEnc(self):
        """"""
        done   = True
        if self.o.outputfile is None : 
            self.o.outputfile = Sys.basename(self.a[1])+Kirmah.EXT

        d        = self.getDefaultOption((self.o.compress,self.o.fullcompress,self.o.nocompress))        
        compress = (KirmahHeader.COMP_END if d == 0 or (d is None and Io.is_binary(self.a[1])) else (KirmahHeader.COMP_ALL if d==1 or d is None else KirmahHeader.COMP_NONE))                
        random   = True if (self.o.random is None and self.o.norandom is None) or self.o.random else False        
        mix      = True if (self.o.mix is None and self.o.nomix is None) or self.o.mix else False

        if (self.o.multiprocess is not None and not represents_int(self.o.multiprocess)) or (not self.o.multiprocess is None and not(int(self.o.multiprocess)>=2 and int(self.o.multiprocess) <=8)) :
            self.parser.error_cmd((('invalid option ',('-j, --multiprocess', Sys.Clz.fgb3), ' value (', ('2',Sys.Clz.fgb3),' to ', ('8',Sys.Clz.fgb3),')'),))

        nproc = int(self.o.multiprocess) if not self.o.multiprocess is None and int(self.o.multiprocess)>=2 and int(self.o.multiprocess) <=8 else 1        

        if not self.o.quiet : self.parser.print_header() 
        
        if Io.file_exists(self.o.outputfile) and not self.o.force:
            Sys.pwarn((('the file ',(self.o.outputfile, Sys.Clz.fgb3), ' already exists !'),))
            done  = Sys.pask('Are you sure to rewrite this file')
            self.stime = Sys.datetime.now()                
        
        if done :
                  
            try :
                if not self.o.quiet and not Sys.g.DEBUG : Sys.print(' Processing, please wait...\n', Sys.Clz.fgB2)
                
                key    = Io.get_data(self.o.keyfile)
                km     = Kirmah(key, None, compress, random, mix)
                
                if nproc > 1 :
                    from gi.repository.Gdk  import threads_enter, threads_leave
                    from gi.repository.GLib import threads_init
                    from gi.repository.Gtk  import main as gtk_main, main_quit as gtk_quit
                    
                    threads_init()
                    threads_enter()
                    kctrl = KCtrl(nproc, None) 
                    kctrl.encrypt(self.a[1], self.o.outputfile, km, None, self.onend_mproc)
                    gtk_main()
                    threads_leave()

                else :            
                    km.encrypt(self.a[1],self.o.outputfile)

            except Exception as e :
                done = False
                print(e)
                pass

        if not self.o.quiet : 
            self.onend_cmd('Encrypting file', self.stime, done, self.o.outputfile)


    def onCommandDec(self):
        """"""
        done  = True
        if self.o.outputfile is None : 
            self.o.outputfile = self.a[1][:-4] if self.a[1][-4:] == Kirmah.EXT else self.a[1]
            
        if not self.o.quiet : self.parser.print_header()
        
        if Io.file_exists(self.o.outputfile) and not self.o.force:
            Sys.pwarn((('the file ',(self.o.outputfile, Sys.Clz.fgb3), ' already exists !'),))
            done  = Sys.pask('Are you sure to rewrite this file')
            self.stime = Sys.datetime.now()                
        
        if done :
        
            try :
                
                if (self.o.multiprocess is not None and not represents_int(self.o.multiprocess)) or (not self.o.multiprocess is None and not(int(self.o.multiprocess)>=2 and int(self.o.multiprocess) <=8)) :
                    self.parser.error_cmd((('invalid option ',('-j, --multiprocess', Sys.Clz.fgb3), ' value (', ('2',Sys.Clz.fgb3),' to ', ('8',Sys.Clz.fgb3),')'),))

                nproc = int(self.o.multiprocess) if not self.o.multiprocess is None and int(self.o.multiprocess)>=2 and int(self.o.multiprocess) <=8 else 1
                
                if not self.o.quiet and not Sys.g.DEBUG : Sys.print(' Processing, please wait...\n', Sys.Clz.fgB2)
                
                key    = Io.get_data(self.o.keyfile)
                km     = Kirmah(key)
                
                if nproc > 1 :
                    from gi.repository.Gdk  import threads_enter, threads_leave
                    from gi.repository.GLib import threads_init
                    from gi.repository.Gtk  import main as gtk_main, main_quit as gtk_quit
                    
                    threads_init()
                    threads_enter()
                    kctrl = KCtrl(nproc, None) 
                    kctrl.decrypt(self.a[1], self.o.outputfile, km, self.onend_mproc)
                    gtk_main()
                    threads_leave()

                else :            
                    km.decrypt(self.a[1],self.o.outputfile)
             
            except BadKeyException as e :
                done = False
                Sys.pwarn(('BadKeyException',))
                if Sys.g.DEBUG : 
                    raise e
        
        if not self.o.quiet : 
            self.onend_cmd('Decrypting file', self.stime, done, self.o.outputfile)



    def onCommandSplit(self):
        """"""
        done  = True
        
        if not self.o.parts is None and not(int(self.o.parts)>=12 and int(self.o.parts) <=62) :
            self.error_cmd((('invalid option ',('-p, --parts', Sys.Clz.fgb3), ' value (', ('12',Sys.Clz.fgb3),' to ', ('62',Sys.Clz.fgb3),')'),))
        else : self.o.parts = int(self.o.parts)
        
        if not self.o.quiet : self.parser.print_header()
        if self.o.outputfile is not None :
            if self.o.outputfile[-5:]!='.tark' : self.o.outputfile += '.tark'        
            if Io.file_exists(self.o.outputfile) and not self.o.force:
                Sys.pwarn((('the file ',(self.o.outputfile, Sys.Clz.fgb3), ' already exists !'),))
                done  = Sys.pask('Are you sure to rewrite this file')
                self.stime = Sys.datetime.now()
        
        if done :        
        
            try :
                if not self.o.quiet and not Sys.g.DEBUG : Sys.print(' Processing, please wait...\n', Sys.Clz.fgB2)
                
                key    = Io.get_data(self.o.keyfile)
                km     = Kirmah(key)
                hlst   = km.ck.getHashList(Sys.basename(self.a[1]), self.o.parts, True)
                kcf    = km.splitFile(self.a[1], hlst)
                t      = int(Sys.time())
                times  = (t,t)
                Io.touch(kcf, times)
                for row in hlst['data']:
                    Io.touch(row[1]+km.EXT,times)

                if self.o.outputfile is not None :
                    import tarfile
                    hlst['data'] = sorted(hlst['data'], key=lambda lst: lst[4])
                    with tarfile.open(self.o.outputfile, mode='w') as tar:
                        tar.add(kcf)
                        Io.removeFile(kcf)
                        for row in hlst['data']:
                            tar.add(row[1]+km.EXT)
                            Io.removeFile(row[1]+km.EXT)

            except Exception as e :
                done = False
                if Sys.g.DEBUG : 
                    raise e
                elif not self.o.quiet : 
                    Sys.pwarn((str(e),)) 
        
        if not self.o.quiet : 
            self.onend_cmd('Splitting file', self.stime, done, self.o.outputfile)


    def onCommandMerge(self):
        """"""
        done   = True

        if not self.o.quiet : self.parser.print_header()

        if done :
            try :
                if not self.o.quiet and not Sys.g.DEBUG : Sys.print(' Processing, please wait...\n', Sys.Clz.fgB2)                
                key    = Io.get_data(self.o.keyfile)
                km     = Kirmah(key)
            
                try:
                    import tarfile
                    with tarfile.open(self.a[1], mode='r') as tar:
                        path = Sys.dirname(self.o.outputfile) if self.o.outputfile is not None else '.'
                        tar.extractall(path=path)
                        for tarinfo in tar:
                            if tarinfo.isreg() and tarinfo.name[-4:]=='.kcf':
                                toPath = km.mergeFile(path+Sys.sep+tarinfo.name)
                except :
                    pass
                    toPath = km.mergeFile(self.a[1])

            except Exception as e :
                done = False
                if Sys.g.DEBUG : 
                    raise e
                elif not self.o.quiet : 
                    Sys.pwarn((str(e),)) 

        if not self.o.quiet : 
            self.onend_cmd('Merging file', self.stime, done, toPath)


    def onend_mproc(self, tstart, done):
        """"""
        from gi.repository.Gtk  import main_quit as gtk_quit
        gtk_quit()


    def getDefaultOption(self, args):        
        """"""
        c = None
        for i, a in enumerate(args) :
            if a : 
                c = i 
                break
        return c    

    
    def onend_cmd(self, title, stime, done, outputfile):
        """"""
        if Sys.g.DEBUG : Sys.dprint()   
        Sys.pstep(title, stime, done)
        if done : 
            Sys.print(' '*5+Sys.realpath(outputfile), Sys.Clz.fgB1, False)
            Sys.print(' ('+Sys.getFileSize(outputfile)+')', Sys.Clz.fgB3)    
