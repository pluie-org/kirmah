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


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module conf ~~

from getpass import getuser as getUserLogin

PRG_NAME            = 'Kirmah'
PRG_CLI_NAME        = 'kirmah-cli'
PRG_VERS            = '2.1'
PRG_AUTHOR          = 'a-Sansara'
PRG_COPY            = 'pluie.org 2013'
PRG_WEBSITE         = 'http://kirmah.sourceforge.net'
PRG_LICENSE         = 'GNU GPL v3'
PRG_LICENSE_PATH    = 'gpl.txt'
PRG_LOGO_PATH       = 'kirmah.png'
PRG_LOGO_ICON_PATH  = 'kirmah_ico.png'
PRG_ABOUT_LOGO_SIZE = 160
PRG_ABOUT_COPYRIGHT = '(c) '+PRG_AUTHOR+' - '+PRG_COPY+'  2013'
PRG_ABOUT_COMMENTS  = ''.join(['Kirmah simply encrypt/decrypt files','\n', 'license ',PRG_LICENSE])
PRG_DESC            = """
  Encryption with symmetric-key algorithm Kirmah.
  
  three modes are available to encrypt :
  
    - compression (full / disabled or only final step)
    - random (simulate a random order - based on crypted key - to randomize data)
    - mix (mix data according to a generated map - based on crypted key - with addition of noise)
  
  
  Process is as follow :
  
  for encryption :
    file > [ compression > ] encryption > [randomiz data > mix data > compression > ] file.kmh 
    
    default options depends on file type (binary or text).
      - binary files are compressed only at the end of process
      - text files have a full compression mode
      - random and mix modes are enabled on all files
  
  for decryption :
    file.kmh > [ uncompression > unmix data > unrandomiz data] > decryption > [uncompression > ] file


  multiprocessing is avalaible for reducing encryption/decryption time.


  for encrypt large binary files, a fastest alternative is possible :
  the split command.

  the split command consist on splitting file into severals parts (with noise addition) according to
  a generated map based on the crypted key.
  the map is fully encrypted as a configuration file (.kcf) which is required to merge all parts

  the merge command is the opposite process.
"""
PRG_GLADE_PATH      = 'kirmah.glade'


DEFVAL_NPROC        = 2
DEFVAL_NPROC_MAX    = 8
DEFVAL_NPROC_MIN    = 2
DEFVAL_COMP         = False
DEFVAL_ENCMODE      = True
DEFVAL_MIXDATA      = False
DEFVAL_USER_PATH    = ''.join(['/home/', getUserLogin(), '/'])
DEFVAL_UKEY_PATH    = ''.join([DEFVAL_USER_PATH, '.', PRG_NAME.lower(), '/'])
DEFVAL_UKEY_NAME    = '.default.key'
DEFVAL_UKEY_LENGHT  = 1024
DEFVAL_CRYPT_EXT    = '.kmh'

DEBUG               = True
UI_TRACE            = True
PCOLOR              = True
