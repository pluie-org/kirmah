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

try :
    from inspect        import signature
except :
    # < python 3.3
    signature = None
    pass

from psr.sys     import Sys


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module decorate ~~

def _logs(sign, t=None, enter=True, wColor=False, args=''):
    """"""
    if Sys.g.DEBUG :
        hasBind = Sys.g_has_ui_bind()
        if hasBind : bind_data = []
        if t is not None : 
            bd = Sys.pdate(t.timetuple(), True)
            if hasBind: bind_data += bd

        a, b, c, d, e = ('=> ' if enter else '<= '), '['+str(Sys.getpid())+']', ' '+sign+'(', _formatArgs(args), ') '
        Sys.print(a , Sys.CLZ_IO  , False)
        Sys.print(b , Sys.CLZ_IO if not Sys.g_is_main_proc() else Sys.CLZ_SEC, False)
        Sys.print(c , Sys.CLZ_FUNC, False)
        Sys.print(d , Sys.CLZ_ARGS, False)
        Sys.print(e , Sys.CLZ_FUNC, False)
        if hasBind:
            bd = [(a, 'io'),(b, 'pid' if not Sys.g_is_main_proc() else 'ppid'),(c , 'cfunc' if not Sys.g_is_main_proc() else 'func'),(d , 'args'),(e , 'cfunc' if not Sys.g_is_main_proc() else 'func')]
            bind_data += bd
        if not enter and t is not None :
            bd = Sys.pdelta(t, '', True)
            if hasBind: bind_data += bd
        else : 
            bd = Sys.dprint(dbcall=True)
            if hasBind: bind_data += bd
            #~ if hasBind: bind_data += e
        if hasBind :
            Sys.wlog(bind_data)
            #~ Sys.g.UI_BIND(bind_data)

def _formatArgs(args):
    """"""
    args = list(args)
    for i,a in enumerate(args) :
        if not (isinstance(a, str) or isinstance(a, bytes)):
            a = str(a)
        if len(a) > 30 :
            args[i] = a[:30]+'...' if isinstance(a, str) else b'...'
    args = str(args)[1:-1]
    if args[-1:] == ',' : args = args[:-1]
    return args

def log(func):
    """"""
    debug  = True
    wcolor = True
    wtime  = True
    """"""
    def wrapped_func(*args, **kwargs):
        """"""
        if debug : 
            t = None if not wtime else Sys.datetime.now()
            # >= python 3.3
            if signature is not None :
                l = [p.name for p in signature(func).parameters.values()]
            # < python 3.3
            # !! BAD FIX !!
            else :
                l = ['self' if args[0].__class__ is not None  else '']
                
            n = args
            if len(n)>0 and l[0] == 'self':
                n = n[1:]
                s = args[0].__class__.__name__ +'.'+func.__name__
            else:
                s = func.__name__
            _logs(s, t, True, wcolor, n)
        f  = func(*args, **kwargs)
        if debug : _logs(s, t, False, wcolor)
        return f
    return wrapped_func
