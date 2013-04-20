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

from psr.io      import Io

def init(name, debug):
    Sys.g_init(name, debug)
    Sys.g_set_main_proc()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Sys ~~

class Sys:
    """"""

    from platform  import system  as getSysName
    from os        import system  as sysCall, remove as removeFile, makedirs, sep, getpid
    from getpass   import getuser as getUserLogin
    from time      import strftime, mktime, time, localtime, sleep
    from datetime  import datetime
    from sys       import exit
    from os.path   import abspath, dirname, join, realpath, basename, getsize, isdir
    from math      import log, floor, ceil
    from ast       import literal_eval
    
    import builtins as g
    
    ERROR   = 'error'
    WARN    = 'warn'
    NOTICE  = 'notice'
    
    g.DEBUG = False
    
    def __init__(self):        
        """"""

    @staticmethod
    def g_init(prjName, debug=False, ui_trace=None, bind=None, color=True):
        Sys.g.PRJ_NAME   = prjName
        Sys.g.DEBUG      = debug
        Sys.g.LOG_FILE   = '.'+prjName+'.log'
        Sys.g.LOG_FO     = Io.wfile(Sys.g.LOG_FILE, False) if bind is not None else None
        #~ Sys.g.LOG_FO.write('# log '+prjName+'\n')
        Sys.g.UI_TRACE   = ui_trace
        Sys.g.UI_BIND    = bind
        Sys.g.COLOR_MODE = color
        #~ Sys.DEBUG      = Debug(True,Debug.NOTICE) 
        from queue      import Queue
        Sys.g.QUEUE      = Queue(0)
        Sys.g.NPQUEUE    = Queue(0)
        Sys.g.MAIN_PROC  = None
    
    @staticmethod
    def g_set_main_proc():
        Sys.g.MAIN_PROC = Sys.getpid()
        
    @staticmethod
    def g_is_main_proc():
        try :
            return Sys.g.MAIN_PROC is None
        except :
            return False    

    @staticmethod
    def g_has_ui_bind():
        try:
            return Sys.g.UI_BIND is not None and Sys.g.DEBUG
        except Exception as e:
            return False

    @staticmethod
    def isUnix():
        """"""
        return not Sys.getSysName() == 'Windows'

    @staticmethod
    def clear():
        return Sys.sysCall('cls' if not Sys.isUnix() else 'clear')

    @staticmethod
    def mkdir_p(path):
        """"""
        try:
            Sys.makedirs(path)
        except OSError as e: # Python >2.5
            if e.errno == Io.EEXIST:
                pass
            else: raise

    @staticmethod
    def readableBytes(b, p=2):
        """Give a human representation of bytes size `b`
        :Returns: `str`
        """
        units = ['B', 'KiB', 'MiB', 'GiB', 'TiB']; 
        b = max(b,0);
        if b == 0 : lb= 0
        else : lb    = Sys.log(b) 
        p = Sys.floor(lb/Sys.log(1024))
        p = min(p, len(units)- 1) 
        #Uncomment one of the following alternatives
        b /= pow(1024,p)
        #b /= (1 << (10 * p)) 
        return str(round(b, 1))+' '+units[p] 
    
    @staticmethod
    def getFileSize(path):
        """"""
        return Sys.readableBytes(Sys.getsize(path))

    @staticmethod
    def getPrintableBytes(bdata):
        """"""
        data = ''
        if isinstance(bdata,bytes) :
            try:
                data = str(bdata, 'utf-8')
            except Exception as e:
                hexv = []
                for i in bdata[1:] :
                    hexv.append(hex(i)[2:].rjust(2,'0'))
                data = ' '.join(hexv)
                pass
        else :
            data = bdata
        return data

    @staticmethod
    def getHexaBytes(bdata):
        """"""
        data = ''
        if isinstance(bdata,bytes) :
            hexv = []
            for i in bdata[1:] :
                hexv.append(hex(i)[2:].rjust(2,'0'))
                data = ' '.join(hexv)
        else :
            data = bdata
        return data

    @staticmethod
    def wlog(data):
        """"""
        Sys.g.LOG_FO.write(str(data)+'\n')
    
    @staticmethod
    def print(data, colors, endLF=True, endClz=True):
        """"""
        if isinstance(data,bytes) :
            data = Sys.getPrintableBytes(data)        

        ev = '' if not endLF else Sys.Clz._LF
        tokens = [c.lstrip(Sys.Clz._MARKER[0]).rstrip(Sys.Clz._SEP) for c in colors.split(Sys.Clz._MARKER) if c is not '']
        if Sys.isUnix() :
            if data is None: data = ''
            if endClz : data += Sys.Clz._uOFF
            if Sys.g.COLOR_MODE :
                Sys.dprint(eval('Sys.Clz._u'+'+Sys.Clz._u'.join(tokens))+data,end=ev, dbcall=True)
            else :
                Sys.dprint(data,end=ev, dbcall=True)
        else :
            if Sys.g.COLOR_MODE : Sys.Clz.setColor(eval('Sys.Clz._w'+'|Sys.Clz._w'.join(tokens)))
            Sys.dprint(data,end=ev, dbcall=True)
            stdout.flush()
            if endClz and Sys.g.COLOR_MODE : Sys.Clz.setColor(Sys.Clz._wOFF)
        #~ else: 
            #~ self.dprint(data,end=ev)

    @staticmethod
    def dprint(d='',end='\n', dbcall=False):
        """"""
        print(d,end=end)
        if Sys.g_has_ui_bind():
            bdata = [(d,'default')]
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def eprint(d='', label='warn', dbcall=False):
        """"""
        c = Sys.CLZ_ERROR if label is Sys.ERROR else Sys.CLZ_WARN
        Sys.print(' '+label+' : ', c, False, False)
        Sys.print(str(d)+' ', c, True, True)
        if Sys.g_has_ui_bind():
            bdata = [(label+' : ' , label),(str(d)+' ', label)]
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def pdate(t, dbcall = False):
        """"""
        t, s = Sys.strftime('%H:%M',t), Sys.strftime(':%S ',t)
        Sys.print(t , Sys.CLZ_TIME, False)
        Sys.print(s , Sys.CLZ_SEC , False)
        if Sys.g_has_ui_bind():
            bdata = [(t , 'time'),(s , 'sec')]
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def pkval(label, value, pad=40, dbcall= False):
        """"""
        l, v = label.rjust(pad,' '), ' '+str(value)        
        Sys.print(l, Sys.CLZ_SEC  , False)
        Sys.print(v, Sys.CLZ_TIME , True)
        if Sys.g_has_ui_bind():
            bdata = [(l, 'sec'),(v, 'time')]
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def pdelta(t, label='', dbcall= False):
        """"""
        if len(label)>0 : Sys.print(label+' ', Sys.CLZ_IO, False)                
        v = ''.join(["{:.5f}".format(Sys.time()-(Sys.mktime(t.timetuple())+1e-6*t.microsecond)),' s'])
        Sys.print(v, Sys.CLZ_DELTA)        
        if Sys.g_has_ui_bind():
            bdata = []
            if len(label)>0 :
                bdata.append((label+' ', 'io'))
            bdata.append((v, 'delta'))
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def pcontent(content, color=None, bcolor='default', dbcall= False):
        """"""
        Sys.print(content, Sys.CLZ_SEC if color is None else color)
        if Sys.g_has_ui_bind():
            bdata = [(content, bcolor)]
            if not dbcall :
                Sys.wlog(bdata)
            else :
                return bdata

    @staticmethod
    def pwarn(data, isError=False, length=120):
        """ data struct : 
          ( # line0               
            'simple line', # LF
            # line1
            #    p0                   p1                      p2
             ('complex line with ',('paramValue',fgcolor), ' suit complex line'), # LF 
            # line2
             'other simple line '
          )
        """
        w  = ' WARNING : ' if not isError else ' ERROR : '
        bg = Sys.Clz.bg5 if not isError else Sys.Clz.bg1
        
        Sys.print(w, bg+Sys.Clz.fgb3, False, False)
        for i, line in enumerate(data) :
            if i > 0 : 
                Sys.print(' '*len(w), bg+Sys.Clz.fgb7, False, False)
            if isinstance(line,str) :
               Sys.print(line.ljust(length-len(w),' '), bg+Sys.Clz.fgb7, True, True)
            else :
                sl = 0
                for p in line : 
                    if isinstance(p,str) :
                        Sys.print(p, bg+Sys.Clz.fgb7, False, False)
                        sl += len(p)
                    else :
                        Sys.print(p[0], bg+p[1], False, False)
                        sl += len(p[0])
                Sys.print(' '.ljust(length-sl-len(w),' '), bg+Sys.Clz.fgb7, True, True)
            
        Sys.dprint()
    
    @staticmethod
    def _psymbol(ch):
        """"""
        Sys.print(' ', Sys.Clz.fgb7, False, False)
        Sys.print(' '+ch+' ',  Sys.Clz.BG4+Sys.Clz.fgb7, False, True)
        Sys.print(' ', Sys.Clz.fgb7, False, True)
    
    @staticmethod
    def pask(ask, yesValue='yes', noValue='no'):
        """"""
        Sys._psymbol('?')
        Sys.print('', Sys.Clz.fgb3, False, False)
        ask    = ask + ' ('+yesValue+'/'+noValue+') ? '
        answer = input(ask)
        while answer.lower()!=yesValue.lower() and answer.lower()!=noValue.lower() :
            s = 'Please enter either '+yesValue+' or '+noValue+' : '
            answer = input(' '.ljust(5,' ')+s.ljust(len(ask),' '))
        Sys.dprint()
        return answer.lower()==yesValue.lower()
    
    @staticmethod
    def pstep(title, stime, done, exitOnFailed=True, length=120):
        """"""
        if stime is not None :
            v = ' ('+''.join(["{:.5f}".format(Sys.time()-(Sys.mktime(stime.timetuple())+1e-6*stime.microsecond)),' s'])+')'
        else : v = ''
        Sys._psymbol('¤')        
        Sys.print(title, Sys.Clz.fgB7, False, False)
        Sys.print(v+' '.ljust(length-len(title)-20-len(v), ' '),Sys.CLZ_DELTA, False, True)
        if done : 
            Sys.print(' ==  OK  == ', Sys.Clz.bg2+Sys.Clz.fgb7)
        else :
            Sys.print(' ==  KO  == ', Sys.Clz.bg1+Sys.Clz.fgb7)
        Sys.dprint()
        if exitOnFailed and not done:
            #~ Sys.dprint(' '.ljust(length-14, ' '),end='')
            #~ Sys.print(' == EXIT == ', Sys.Clz.bg1+Sys.Clz.fgb7)
            #~ Sys.dprint()
            Sys.exit(1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Coloriz ~~

class Coloriz:

    _MARKER        = '!§'
    """"""
    _SEP           = ';'
    """"""
    _PATTERN_COLOR = '^'+_MARKER[0]+'[nfNFbB][0-7]'+_SEP+'$'
    """"""
    _wFH   = 0x0008
    """"""
    _wBH   = 0x0080
    """"""
    _uOFF  = '\033[1;m'
    """"""
    _wOFF  = None
    """"""
    _LF    = '\n'
    """"""
    OFF    = _MARKER+_MARKER[0]+'OFF'+_SEP+_MARKER
    """"""    
    def __init__(self):
        """Colors for both plateform are : 0: black - 1: red - 2:green - 3: yellow - 4: blue - 5: purple - 6: cyan - 7: white 
        available class members :
        foreground normal (same as bold for w32): 
           self.fgn0 -> self.fgn7
        foreground bold :
           self.fgb0 -> self.fgb7
        foreground high intensity (same as bold high intensity for w35):
           self.fgN0 -> self.fgN7
        foreground bold high intensity :
           self.fgB0 -> self.fgB7
        background
           self.bg0 -> self.bg7
        background high intensity
           self.BG0 -> self.BG7
        default colors :
            self.OFF
        
            usage : 
            pc = PColor()
            pc.print('%smon label%s:%sma value%s' % (pc.BG4+pc.fgN7, pc.OFF+pc.fgn1, pc.fgb4, pc.OFF))
        """
        global Sys

        if not Sys.isUnix():
            j = 0
            for i in (0,4,2,6,1,5,3,7):
                exec('self._wf%i = 0x000%i' % (i,j) + '\nself._wb%i = 0x00%i0' % (i,j) + '\nself._wF%i = 0x000%i | self._wFH' % (i,j) + '\nself._wB%i = 0x00%i0 | self._wBH' % (i,j))
                # normal eq bold
                exec('self._wn%i = self._wf%i' % (i,i))
                # normal high intensity eq bold high intensity
                exec('self._wN%i = self._wF%i' % (i,i))
                j += 1
            import impra.w32color as w32cons
            self._wOFF    = w32cons.get_text_attr()
            self._wOFFbg  = self._wOFF & 0x0070
            self._wOFFfg  = self._wOFF & 0x0007
            self.setColor = w32cons.set_text_attr

        for i in range(0,8):            
            # foreground normal
            exec('self.fgn%i = self._MARKER + self._MARKER[0] + "n%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._un%i = "\\033[0;3%im"' % (i,i))
            # foreground bold
            exec('self.fgb%i = self._MARKER + self._MARKER[0] + "f%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._uf%i = "\\033[1;3%im"' % (i,i))
            # foreground high intensity
            exec('self.fgN%i = self._MARKER + self._MARKER[0] + "N%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._uN%i = "\\033[0;9%im"' % (i,i))
            # foreground bold high intensity
            exec('self.fgB%i = self._MARKER + self._MARKER[0] + "F%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._uF%i = "\\033[1;9%im"' % (i,i))
            # background 
            exec('self.bg%i = self._MARKER + self._MARKER[0] + "b%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._ub%i = "\\033[4%im"' % (i,i))
            # background high intensity
            exec('self.BG%i = self._MARKER + self._MARKER[0] + "B%i" + self._SEP + self._MARKER' % (i,i))
            if True or Sys.isUnix() : exec('self._uB%i = "\\033[0;10%im"' % (i,i))

Sys.Clz         = Coloriz() 
Sys.CLZ_TIME    = Sys.Clz.fgN2+Sys.Clz.bg0
Sys.CLZ_SEC     = Sys.Clz.fgb7+Sys.Clz.bg0
Sys.CLZ_IO      = Sys.Clz.fgB1+Sys.Clz.bg0
Sys.CLZ_FUNC    = Sys.Clz.fgb3+Sys.Clz.bg0
Sys.CLZ_ARGS    = Sys.Clz.fgn7+Sys.Clz.bg0
Sys.CLZ_DELTA   = Sys.Clz.fgN4+Sys.Clz.bg0
Sys.CLZ_ERROR   = Sys.Clz.fgb7+Sys.Clz.bg1
Sys.CLZ_WARN    = Sys.Clz.fgb7+Sys.Clz.bg5
Sys.CLZ_DEFAULT = Sys.Clz.fgb7+Sys.Clz.bg0
