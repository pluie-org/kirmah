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
# ~~ package cli ~~
    
from    optparse        import OptionParser, OptionGroup
import  kirmah.conf     as conf
from    kirmah.cliapp   import CliApp
from    psr.sys         import Sys
from    psr.io          import Io


LINE_SEP_LEN  = 120
LINE_SEP_CHAR = '―'
if not Sys.isUnix : LINE_SEP_CHAR = '-'


def printLineSep(sep,lenSep):
    """"""
    Sys.print(sep*lenSep, Sys.Clz.fgN0)
def printHeaderTitle(title):
    """"""
    Sys.print(' == '+title+' == ', Sys.Clz.BG4+Sys.Clz.fgB7, False, True)

def printHeaderPart(label,value):
    """"""
    Sys.print(' [' , Sys.Clz.fgB0, False)
    Sys.print(label, Sys.Clz.fgB3, False)
    Sys.print(':'  , Sys.Clz.fgB0, False)
    Sys.print(value, Sys.Clz.fgB4, False)
    Sys.print('] ' , Sys.Clz.fgB0, False)



class _OptionParser(OptionParser):
    """A simplified OptionParser"""
    
    def format_description(self, formatter):
        return self.description

    def format_epilog(self, formatter):
        return self.epilog
        
    def error(self, errMsg, errData=None):
        
        self.print_usage('')
        Cli.error_cmd(self, (errMsg,))
        #~ Sys.exit(1)


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Cli ~~

class Cli:
    
    def __init__(self,path):
        """"""
        
        self.HOME   = Sys.sep+'home'+Sys.sep+Sys.getUserLogin()+Sys.sep
        self.DIRKEY = self.HOME+'.'+conf.PRG_NAME.lower()+Sys.sep
        if not Sys.isUnix() :
            CHQ     = '"'
            self.HOME   = 'C:'+Sys.sep+conf.PRG_NAME.lower()+Sys.sep
            self.DIRKEY = self.HOME+'keys'+Sys.sep
        Sys.mkdir_p(self.DIRKEY)        
        
        #~ self.ini    = util.IniFile(path+'impra.ini')
        parser             = _OptionParser()
        parser.print_help  = self.print_help
        parser.print_usage = self.print_usage

        gpData             = OptionGroup(parser, '')

        # metavar='<ARG1> <ARG2>', nargs=2
        parser.add_option('-v', '--version'       , action='store_true', default=False)
        parser.add_option('-d', '--debug'         , action='store_true', default=False)
        parser.add_option('-f', '--force'         , action='store_true', default=False)
        parser.add_option('-q', '--quiet'         , action='store_true', default=False)
        
        parser.add_option('--no-color'            , action='store_true' , default=False)
        
        gpData.add_option('-a', '--fullcompress'  , action='store_true' )
        gpData.add_option('-z', '--compress'      , action='store_true' )
        gpData.add_option('-Z', '--nocompress'    , action='store_true' )
        gpData.add_option('-r', '--random'        , action='store_true' )
        gpData.add_option('-R', '--norandom'      , action='store_true' )
        gpData.add_option('-m', '--mix'           , action='store_true' )
        gpData.add_option('-M', '--nomix'         , action='store_true' )
        gpData.add_option('-j', '--multiprocess'  , action='store')
        gpData.add_option('-k', '--keyfile'       , action='store')
        gpData.add_option('-l', '--length'        , action='store', default=1024)
        gpData.add_option('-p', '--parts'         , action='store', default=22)
        gpData.add_option('-o', '--outputfile'    , action='store')
        parser.add_option_group(gpData)

        (o, a) = parser.parse_args()
        
        Sys.g.COLOR_MODE = not o.no_color   
        Sys.g.DEBUG      = o.debug and not o.quiet

        if not a:

            try :
                if not o.help :
                    self.error_cmd(('no command specified',))
                else :
                    Sys.clear()
                    parser.print_help()
            except :
                self.error_cmd(('no command specified',))

        else:   
            
            if a[0] == 'help':
                Sys.clear()
                parser.print_help()

            elif a[0] in ['key','enc','dec','split','merge'] :

                app = CliApp(self.HOME, path, self, a, o) 

                if a[0]=='key'  : 
                    app.onCommandKey()
                else :
                    if not len(a)>1   : 
                        self.error_cmd((('an ',('inputFile',Sys.Clz.fgb3),' is required !'),)) 
                    elif not Io.file_exists(a[1]):                    
                        self.error_cmd((('the file ',(a[1], Sys.Clz.fgb3), ' doesn\'t exists !'),)) 

                    elif a[0]=='enc'  : app.onCommandEnc()
                    elif a[0]=='dec'  : app.onCommandDec()
                    elif a[0]=='split': app.onCommandSplit()
                    elif a[0]=='merge': app.onCommandMerge()
            else :
                self.error_cmd((('unknow command ',(a[0],Sys.Clz.fgb3)),))

        if not o.quiet : Sys.dprint()


    def error_cmd(self, data):
        """"""
        self.print_usage('')
        Sys.dprint()
        Sys.pwarn(data, True)
        self.exit(1)


    def exit(self, code):
        """"""
        if Sys.isUnix() : Sys.exit(code)


    def print_header(self):
        """"""       
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        printHeaderTitle(conf.PRG_CLI_NAME)
        printHeaderPart('version'  ,conf.PRG_VERS)
        printHeaderPart('author'   ,conf.PRG_AUTHOR)
        printHeaderPart('license'  ,conf.PRG_LICENSE)
        printHeaderPart('copyright',conf.PRG_COPY)        
        Sys.print(' ', Sys.Clz.OFF)
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.dprint()


    def print_version(self, data):
        """"""
        self.print_header()


    def print_usage(self, data, withoutHeader=False):
        """"""
        if not withoutHeader : self.print_header()
  
        Sys.print('  USAGE :\n'                , Sys.Clz.fgB3)
        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('help '                  , Sys.Clz.fgB3)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('key   '                     , Sys.Clz.fgB3, False)
        Sys.print('[ -l '                      , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('length'                     , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -o '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('outputFile'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(']'                          , Sys.Clz.fgB3)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('enc   '                     , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('inputFile'                  , Sys.Clz.fgB1, False)
        Sys.print('} '                         , Sys.Clz.fgB1, False)
        Sys.print('['                          , Sys.Clz.fgB3, False)
        Sys.print(' -z|Z|a -r|R -m|M -j '      , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('numProcess'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -k '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('keyFile'                    , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -o '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('outputFile'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(']'                          , Sys.Clz.fgB3)
        
        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('dec   '                     , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('inputFile'                  , Sys.Clz.fgB1, False)
        Sys.print('} '                         , Sys.Clz.fgB1, False)
        Sys.print('['                          , Sys.Clz.fgB3, False)
        Sys.print(' -j '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('numProcess'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -k '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('keyFile'                    , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -o '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('outputFile'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(']'                          , Sys.Clz.fgB3)
        
        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('split '                     , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('inputFile'                  , Sys.Clz.fgB1, False)
        Sys.print('} '                         , Sys.Clz.fgB1, False)
        Sys.print('['                          , Sys.Clz.fgB3, False)
        Sys.print(' -p '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('numParts'                   , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -k '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('keyFile'                    , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -o '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('tarOutputFile'              , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(']'                          , Sys.Clz.fgB3)
        
        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.Clz.fgb7, False)
        Sys.print('merge '                     , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('inputFile'                  , Sys.Clz.fgB1, False)
        Sys.print('} '                         , Sys.Clz.fgB1, False)
        Sys.print('['                          , Sys.Clz.fgB3, False)
        Sys.print(' -k '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('keyFile'                    , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(' -o '                       , Sys.Clz.fgB3, False)
        Sys.print('{'                          , Sys.Clz.fgB1, False)
        Sys.print('outputFile'                 , Sys.Clz.fgB1, False)
        Sys.print('}'                          , Sys.Clz.fgB1, False)
        Sys.print(']'                          , Sys.Clz.fgB3)

    
    def print_options(self):
        """"""
        Sys.dprint('\n')
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)

        Sys.print('  MAIN OPTIONS :\n'                                       , Sys.Clz.fgB3)        
        Sys.print(' '*4+'-v'.ljust(13,' ')+', --version'                     , Sys.Clz.fgB3)
        Sys.print(' '*50+'display programm version'                          , Sys.Clz.fgB7)
        Sys.print(' '*4+'-d'.ljust(13,' ')+', --debug'                       , Sys.Clz.fgB3)
        Sys.print(' '*50+'enable debug mode'                                 , Sys.Clz.fgB7)
        Sys.print(' '*4+'-f'.ljust(13,' ')+', --force'                       , Sys.Clz.fgB3)
        Sys.print(' '*50+'force rewriting existing files without alert'      , Sys.Clz.fgB7)
        Sys.print(' '*4+'-q'.ljust(13,' ')+', --quiet'                       , Sys.Clz.fgB3)
        Sys.print(' '*50+'don\'t print status messages to stdout'            , Sys.Clz.fgB7)
        Sys.print(' '*4+'-h'.ljust(13,' ')+', --help'                        , Sys.Clz.fgB3)
        Sys.print(' '*50+'display help'                                      , Sys.Clz.fgB7)   
        
        Sys.dprint('\n')
        Sys.print('  KEY OPTIONS :\n'                                        , Sys.Clz.fgB3)
        Sys.print(' '*4+'-l '                                                , Sys.Clz.fgB3, False)
        Sys.print('LENGTH'.ljust(10,' ')                                     , Sys.Clz.fgB1, False)
        Sys.print(', --length'.ljust(18,' ')                                 , Sys.Clz.fgB3, False)
        Sys.print('LENGTH'.ljust(10,' ')                                     , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified key length (128 to 4096 - default:1024)' , Sys.Clz.fgB7)  
        Sys.print(' '*4+'-o '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified key output filename'                     , Sys.Clz.fgB7)
        
        Sys.dprint('\n')        
        Sys.print('  ENCRYPT OPTIONS :\n'                                    , Sys.Clz.fgB3)
        Sys.print(' '*4+'-a'.ljust(13,' ')+', --fullcompress'                , Sys.Clz.fgB3)
        Sys.print(' '*50+'enable full compression mode'                      , Sys.Clz.fgB7)
        Sys.print(' '*4+'-z'.ljust(13,' ')+', --compress'                    , Sys.Clz.fgB3)
        Sys.print(' '*50+'enable compression mode'                           , Sys.Clz.fgB7)
        Sys.print(' '*4+'-Z'.ljust(13,' ')+', --nocompress'                  , Sys.Clz.fgB3)
        Sys.print(' '*50+'disable compression mode'                          , Sys.Clz.fgB7)
        Sys.print(' '*4+'-r'.ljust(13,' ')+', --random'                      , Sys.Clz.fgB3)
        Sys.print(' '*50+'enable random mode'                                , Sys.Clz.fgB7)
        Sys.print(' '*4+'-R'.ljust(13,' ')+', --norandom'                    , Sys.Clz.fgB3)
        Sys.print(' '*50+'disable random mode'                               , Sys.Clz.fgB7)
        Sys.print(' '*4+'-m'.ljust(13,' ')+', --mix'                         , Sys.Clz.fgB3)
        Sys.print(' '*50+'enable mix mode'                                   , Sys.Clz.fgB7)
        Sys.print(' '*4+'-M'.ljust(13,' ')+', --nomix'                       , Sys.Clz.fgB3)
        Sys.print(' '*50+'disable mix mode'                                  , Sys.Clz.fgB7)
        Sys.print(' '*4+'-j '                                                , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1, False)
        Sys.print(', --multiprocess'.ljust(18,' ')                           , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1)
        Sys.print(' '*50+'number of process for encryption (2 to 8)'         , Sys.Clz.fgB7) 
        Sys.print(' '*4+'-k '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'key filename used to encrypt'                      , Sys.Clz.fgB7)
        Sys.print(' '*4+'-o '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified encrypted output filename'               , Sys.Clz.fgB7)        
        
        Sys.dprint('\n')        
        Sys.print('  DECRYPT OPTIONS :\n'                                    , Sys.Clz.fgB3)
        Sys.print(' '*4+'-j '                                                , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1, False)
        Sys.print(', --multiprocess'.ljust(18,' ')                           , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1)
        Sys.print(' '*50+'number of process for decryption (2 to 8)'         , Sys.Clz.fgB7) 
        Sys.print(' '*4+'-k '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'key filename used to decrypt'                      , Sys.Clz.fgB7)        
        Sys.print(' '*4+'-o '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified decrypted output filename'               , Sys.Clz.fgB7)

        Sys.dprint('\n')        
        Sys.print('  SPLIT OPTIONS :\n'                                      , Sys.Clz.fgB3)
        Sys.print(' '*4+'-p '                                                , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1, False)
        Sys.print(', --part'.ljust(18,' ')                                   , Sys.Clz.fgB3, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.Clz.fgB1)
        Sys.print(' '*50+'count part to split'                               , Sys.Clz.fgB7)
        Sys.print(' '*4+'-k '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'key filename used to split'                        , Sys.Clz.fgB7)        
        Sys.print(' '*4+'-o '                                                , Sys.Clz.fgB3, False)
        Sys.print('TARFILE'.ljust(10,' ')                                    , Sys.Clz.fgB1, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.Clz.fgB3, False)
        Sys.print('TARFILE'.ljust(10,' ')                                    , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified tar output filename'                     , Sys.Clz.fgB7)

        Sys.dprint('\n')        
        Sys.print('  MERGE OPTIONS :\n'                                      , Sys.Clz.fgB3)
        Sys.print(' '*4+'-k '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'key filename used to merge'                        , Sys.Clz.fgB7)
        Sys.print(' '*4+'-o '                                                , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.Clz.fgB3, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.Clz.fgB1)
        Sys.print(' '*50+'specified decrypted output filename'               , Sys.Clz.fgB7)
        
        Sys.dprint('\n')    


    def print_help(self):
        """"""

        self.print_header()
        Sys.print(conf.PRG_DESC, Sys.Clz.fgN1)
        self.print_usage('',True)
        self.print_options()
        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.dprint()
        Sys.print('  EXEMPLES :\n', Sys.Clz.fgB3)
        CHQ  = "'"
        
        Sys.print(' '*4+'command key :', Sys.Clz.fgB3)        
        
        Sys.print(' '*8+'# generate a new crypted key of 2048 length', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('key -l ', Sys.Clz.fgB3, False)
        Sys.print('2048 ', Sys.Clz.fgB1)

        Sys.print(' '*8+'# generate a new crypted key (default length is 1024) in a specified location', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('key -o ', Sys.Clz.fgB3, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.Clz.fgB1)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command encrypt :', Sys.Clz.fgB3)
        
        Sys.print(' '*8+'# encrypt specified file with default crypted key and default options', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('enc ', Sys.Clz.fgB3, False)
        Sys.print(self.HOME+'mySecretTextFile.txt', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# encrypt specified file with specified crypted key (full compression, no random but mix mode)', Sys.Clz.fgn7)
        Sys.print(' '*8+'# on specified output location', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('enc ', Sys.Clz.fgB3, False)
        Sys.print('mySecretTextFile.txt', Sys.Clz.fgB1, False)
        Sys.print(' -aRm -k ' , Sys.Clz.fgB3, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.Clz.fgB1, False)
        Sys.print(' -o ' , Sys.Clz.fgB3, False)
        Sys.print('test.kmh', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# encrypt specified file with default crypted key (no compression but random & mix mode and multiprocessing)', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('enc ', Sys.Clz.fgB3, False)
        Sys.print('myBigTextFile.txt', Sys.Clz.fgB1, False)
        Sys.print(' -Zrm -j ' , Sys.Clz.fgB3, False)
        Sys.print('4', Sys.Clz.fgB1)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command decrypt :', Sys.Clz.fgB3)
        
        Sys.print(' '*8+'# decrypt specified file with default crypted key', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('dec ', Sys.Clz.fgB3, False)
        Sys.print(self.HOME+'mySecretFile.kmh', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# decrypt specified file with specified crypted key on specified output location', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('dec ', Sys.Clz.fgB3, False)
        Sys.print('myEncryptedSecretFile.kmh', Sys.Clz.fgB1, False)
        Sys.print(' -k ' , Sys.Clz.fgB3, False)
        Sys.print(self.HOME+'.kirmah'+Sys.sep+'.myNewKey', Sys.Clz.fgB1, False)        
        Sys.print(' -o ' , Sys.Clz.fgB3, False)
        Sys.print('myDecryptedSecretFile.txt', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# decrypt specified file with default crypted key and multiprocessing', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('dec ', Sys.Clz.fgB3, False)
        Sys.print('myEncryptedSecretFile.kmh', Sys.Clz.fgB1, False)
        Sys.print(' -j ' , Sys.Clz.fgB3, False)
        Sys.print('4'    , Sys.Clz.fgB1)


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command split :', Sys.Clz.fgB3)
        
        Sys.print(' '*8+'# split specified file with default crypted key', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('split ', Sys.Clz.fgB3, False)
        Sys.print(self.HOME+'myBigBinaryFile.avi', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# split specified file on 55 parts with specified crypted key on specified output location', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('split ', Sys.Clz.fgB3, False)
        Sys.print('myBigBinaryFile.avi', Sys.Clz.fgB1, False)
        Sys.print(' -p ' , Sys.Clz.fgB3, False)
        Sys.print('55'   , Sys.Clz.fgB1, False)        
        Sys.print(' -k ' , Sys.Clz.fgB3, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.Clz.fgB1, False)
        Sys.print(' -o ' , Sys.Clz.fgB3, False)
        Sys.print('myBigBinaryFile.encrypted', Sys.Clz.fgB1)        


        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command merge :', Sys.Clz.fgB3)
        
        Sys.print(' '*8+'# merge specified splitted file with default crypted key', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('merge ', Sys.Clz.fgB3, False)
        Sys.print(self.HOME+'6136bd1b53d84ecbad5380594eea7256176c19e0266c723ea2e982f8ca49922b.kcf', Sys.Clz.fgB1)
        
        Sys.print(' '*8+'# merge specified tark splitted file with specified crypted key on specified output location', Sys.Clz.fgn7)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.Clz.fgB7, False)
        Sys.print('merge ', Sys.Clz.fgB3, False)
        Sys.print('myBigBinaryFile.encrypted.tark', Sys.Clz.fgB1, False)
        Sys.print(' -k ' , Sys.Clz.fgB3, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.Clz.fgB1, False)
        Sys.print(' -o ' , Sys.Clz.fgB3, False)
        Sys.print('myBigBinaryFile.decrypted.avi', Sys.Clz.fgB1)

        printLineSep(LINE_SEP_CHAR,LINE_SEP_LEN)
        Sys.dprint()
