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


from gi.repository.GObject  import timeout_add
from psr.sys                import Sys
from psr.mproc              import Ctrl
from psr.decorate           import log
from kirmah.crypt           import Kirmah, ConfigKey, KeyGen, b2a_base64, a2b_base64, hash_sha256


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class KCtrl ~~

class KCtrl(Ctrl):
   
    @log
    def encrypt(self, fromPath, toPath, km, header=None, callback=None, timeout=50):
        """"""
        self.tstart   = Sys.datetime.now()
        self.km       = km        
        self.callback = callback
        self.fromPath = fromPath
        self.toPath   = toPath
        
        if Sys.g.DEBUG : Sys.pcontent(' Encrypting file : '+self.fromPath+' ('+Sys.getFileSize(self.fromPath)+') by '+str(self.nproc)+' process')
        if self.nproc < 2:
            self.km.encrypt(self.fromPath, self.toPath, header)            
            self.on_end_mpenc()
        else :
            self.ppid = Sys.getpid()
            self.fp, self.tp, self.rmode, self.mmode, self.compend = self.km.encrypt_sp_start(fromPath, toPath, header)
            self.hsltPaths = self.km.prepare_mproc_encode(self.fp, self.nproc)
            self.bind_task(self.mpenc)
            self.start(timeout, None, self.on_end_mpenc)

    @log
    def decrypt(self, fromPath, toPath, km, callback=None, timeout=50):
        """"""
        self.tstart   = Sys.datetime.now()
        self.km       = km
        self.callback = callback
        self.fromPath = fromPath
        self.toPath   = toPath
        self.ppid = Sys.getpid()
        if Sys.g.DEBUG : Sys.pcontent(' Decrypting file : '+self.fromPath+' ('+Sys.getFileSize(self.fromPath)+') by '+str(self.nproc)+' process')
        if self.nproc < 2:
            self.decrypt(fromPath, toPath)            
            self.on_end_mpdec()
        else :
            self.fp, self.tp, self.compstart = self.km.decrypt_sp_start(fromPath, toPath)
            self.hsltPaths = self.km.prepare_mproc_decode(self.fp, self.nproc)
            self.bind_task(self.mpdec)
            self.start(50, None, self.on_end_mpdec)

    #~ @log
    def getSubStartIndice(self, id):
        """"""
        return sum([ len(x) for j, x in enumerate(self.data) if j < id ])%len(self.km.key)
        
    @log
    def mpenc(self, id):
        """"""
        self.km.mproc_encode_part(id, self.ppid) 

    @log
    def mpdec(self, id):
        """"""
        self.km.mproc_decode_part(id, self.ppid)
        
    @log
    def on_end_mpdec(self):
        """"""
        if self.nproc > 1 :     
            self.km.mpMergeFiles(self.hsltPaths, self.tp)
            self.km.decrypt_sp_end(self.tp, self.toPath, self.compstart)
        if self.callback is not None : self.callback(self.tstart, True)
        
    @log
    def on_end_mpenc(self):
        """"""
        if self.nproc > 1 :
            self.km.mpMergeFiles(self.hsltPaths, self.tp)
            self.fp, self.tp = self.tp, self.km.tmpPath2 if self.tp == self.km.tmpPath1 else self.km.tmpPath1
            self.km.encrypt_sp_end(self.fp, self.tp, self.toPath, self.rmode, self.mmode, self.compend)        
        if self.callback is not None : self.callback(self.tstart, True)
