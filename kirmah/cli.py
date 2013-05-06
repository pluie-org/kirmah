#  !/usr/bin/env python
#  -*- coding: utf-8 -*-
#  kirmah.cli.py
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  software  : Kirmah    <http://kirmah.sourceforge.net/>
#  version   : 2.17
#  date      : 2013
#  licence   : GPLv3.0   <http://www.gnu.org/licenses/>
#  author    : a-Sansara <[a-sansara]at[clochardprod]dot[net]>
#  copyright : pluie.org <http://www.pluie.org/>
#
#  # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#
#  This file is part of Kirmah.
#
#  Kirmah is free software (free as in speech) : you can redistribute it
#  and/or modify it under the terms of the GNU General Public License as
#  published by the Free Software Foundation, either version 3 of the License,
#  or (at your option) any later version.
#
#  Kirmah is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Kirmah.  If not, see <http://www.gnu.org/licenses/>.
#

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ module cli ~~

from    optparse        import OptionParser, OptionGroup
import  kirmah.conf     as conf
from    kirmah.cliapp   import CliApp
from    psr.sys         import Sys, Io, Const, init
from    psr.log         import Log

if not Sys.isUnix : Const.LINE_SEP_CHAR = '-'


def printLineSep(sep,lenSep):
    """"""
    s = sep*lenSep
    Sys.print(s, Sys.CLZ_HEAD_LINE)
    return [(s, Const.CLZ_HEAD_SEP)]


def printHeaderTitle(title):
    """"""
    s = ' == '+title+' == '
    Sys.print(s, Sys.CLZ_HEAD_APP, False, True)
    return [(s, Const.CLZ_HEAD_APP)]


def printHeaderPart(label,value):
    """"""
    a, b, c = ' [',':' ,'] '
    Sys.print(a    , Sys.CLZ_HEAD_SEP, False)
    Sys.print(label, Sys.CLZ_HEAD_KEY, False)
    Sys.print(b    , Sys.CLZ_HEAD_SEP, False)
    Sys.print(value, Sys.CLZ_HEAD_VAL, False)
    Sys.print(c    , Sys.CLZ_HEAD_SEP, False)
    return [(a,Const.CLZ_HEAD_SEP),(label,Const.CLZ_HEAD_KEY),(b,Const.CLZ_HEAD_SEP),(value,Const.CLZ_HEAD_VAL),(c,Const.CLZ_HEAD_SEP)]


class _OptionParser(OptionParser):
    """A simplified OptionParser"""

    def format_description(self, formatter):
        return self.description


    def format_epilog(self, formatter):
        return self.epilog


    def error(self, errMsg, errData=None):
        self.print_usage('')
        Cli.error_cmd(self, (errMsg,))


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~ class Cli ~~

class Cli:

    def __init__(self, path, remote=False, rwargs=None, thread=None, loglvl=Const.LOG_DEFAULT):
        """"""
        if thread is not None :
            Sys.g.THREAD_CLI               = thread
            Sys.g.GUI                      = True
        else :
            Sys.g.GUI = False


        self.HOME   = conf.DEFVAL_USER_PATH
        self.DIRKEY = self.HOME+'.'+conf.PRG_NAME.lower()+Sys.sep
        if not Sys.isUnix() :
            CHQ     = '"'
            self.HOME   = 'C:'+Sys.sep+conf.PRG_NAME.lower()+Sys.sep
            self.DIRKEY = self.HOME+'keys'+Sys.sep
        Sys.mkdir_p(self.DIRKEY)

        parser             = _OptionParser()
        parser.print_help  = self.print_help
        parser.print_usage = self.print_usage

        gpData             = OptionGroup(parser, '')

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

        # rewrite argv sended by remote
        if rwargs is not None :
            import sys
            sys.argv = rwargs

        (o, a) = parser.parse_args()

        Sys.g.QUIET = o.quiet

        init(conf.PRG_NAME, o.debug, remote, not o.no_color, loglvl)

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

                    Sys.dprint('PUT END SIGNAL')
                    if Sys.g.LOG_QUEUE is not None :
                        Sys.g.LOG_QUEUE.put(Sys.g.SIGNAL_STOP)

            else :
                self.error_cmd((('unknow command ',(a[0],Sys.Clz.fgb3)),))

        if not o.quiet : Sys.dprint()


    def clean(self):
        """"""
        print('cleaning')


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
        a = printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        b = printHeaderTitle(conf.PRG_CLI_NAME)
        c = printHeaderPart('version'  ,conf.PRG_VERS)
        d = printHeaderPart('author'   ,conf.PRG_AUTHOR)
        e = printHeaderPart('license'  ,conf.PRG_LICENSE)
        f = printHeaderPart('copyright',conf.PRG_COPY)
        Sys.print(' ', Sys.Clz.OFF)
        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)        
        Sys.wlog(a)
        Sys.wlog(b + c + d + e + f )
        Sys.wlog(a)
        Sys.wlog(Sys.dprint())


    def print_version(self, data):
        """"""
        self.print_header()


    def print_usage(self, data, withoutHeader=False):
        """"""
        if not withoutHeader : self.print_header()

        Sys.print('  USAGE :\n'                , Sys.CLZ_HELP_CMD)
        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('help '                      , Sys.CLZ_HELP_CMD)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('key   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.print('[ -l '                      , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('length'                     , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(']'                          , Sys.CLZ_HELP_ARG)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('enc   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.print('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.print('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.print(' -z|Z|a -r|R -m|M -j '      , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('numProcess'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(']'                          , Sys.CLZ_HELP_ARG)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('dec   '                     , Sys.CLZ_HELP_CMD, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.print('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.print('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.print(' -j '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('numProcess'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(']'                          , Sys.CLZ_HELP_ARG)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('split '                     , Sys.CLZ_HELP_CMD, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.print('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.print('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.print(' -p '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('numParts'                   , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('tarOutputFile'              , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(']'                          , Sys.CLZ_HELP_ARG)

        Sys.print('    '+conf.PRG_CLI_NAME+' ' , Sys.CLZ_HELP_PRG, False)
        Sys.print('merge '                     , Sys.CLZ_HELP_CMD, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('inputFile'                  , Sys.CLZ_HELP_PARAM, False)
        Sys.print('} '                         , Sys.CLZ_HELP_PARAM, False)
        Sys.print('['                          , Sys.CLZ_HELP_ARG, False)
        Sys.print(' -k '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('keyFile'                    , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o '                       , Sys.CLZ_HELP_ARG, False)
        Sys.print('{'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print('outputFile'                 , Sys.CLZ_HELP_PARAM, False)
        Sys.print('}'                          , Sys.CLZ_HELP_PARAM, False)
        Sys.print(']'                          , Sys.CLZ_HELP_ARG)


    def print_options(self):
        """"""
        Sys.dprint('\n')
        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)

        Sys.print('  MAIN OPTIONS :\n'                                       , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-v'.ljust(13,' ')+', --version'                     , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'display programm version'                          , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-d'.ljust(13,' ')+', --debug'                       , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'enable debug mode'                                 , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-f'.ljust(13,' ')+', --force'                       , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'force rewriting existing files without alert'      , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-q'.ljust(13,' ')+', --quiet'                       , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'don\'t print status messages to stdout'            , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-h'.ljust(13,' ')+', --help'                        , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'display help'                                      , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.print('  KEY OPTIONS :\n'                                        , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-l '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('LENGTH'.ljust(10,' ')                                     , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --length'.ljust(18,' ')                                 , Sys.CLZ_HELP_ARG, False)
        Sys.print('LENGTH'.ljust(10,' ')                                     , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified key length (128 to 4096 - default:1024)' , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified key output filename'                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.print('  ENCRYPT OPTIONS :\n'                                    , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-a'.ljust(13,' ')+', --fullcompress'                , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'enable full compression mode'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-z'.ljust(13,' ')+', --compress'                    , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'enable compression mode'                           , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-Z'.ljust(13,' ')+', --nocompress'                  , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'disable compression mode'                          , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-r'.ljust(13,' ')+', --random'                      , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'enable random mode'                                , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-R'.ljust(13,' ')+', --norandom'                    , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'disable random mode'                               , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-m'.ljust(13,' ')+', --mix'                         , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'enable mix mode'                                   , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-M'.ljust(13,' ')+', --nomix'                       , Sys.CLZ_HELP_ARG)
        Sys.print(' '*50+'disable mix mode'                                  , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-j '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --multiprocess'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'number of process for encryption (2 to 8)'         , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'key filename used to encrypt'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified encrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.print('  DECRYPT OPTIONS :\n'                                    , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-j '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --multiprocess'.ljust(18,' ')                           , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'number of process for decryption (2 to 8)'         , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'key filename used to decrypt'                      , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified decrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.print('  SPLIT OPTIONS :\n'                                      , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-p '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --part'.ljust(18,' ')                                   , Sys.CLZ_HELP_ARG, False)
        Sys.print('COUNT'.ljust(10,' ')                                      , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'count part to split'                               , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'key filename used to split'                        , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('TARFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.print('TARFILE'.ljust(10,' ')                                    , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified tar output filename'                     , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')
        Sys.print('  MERGE OPTIONS :\n'                                      , Sys.CLZ_HELP_CMD)
        Sys.print(' '*4+'-k '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --keyfile'.ljust(18,' ')                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'key filename used to merge'                        , Sys.CLZ_HELP_ARG_INFO)
        Sys.print(' '*4+'-o '                                                , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM, False)
        Sys.print(', --outputfile'.ljust(18,' ')                             , Sys.CLZ_HELP_ARG, False)
        Sys.print('FILE'.ljust(10,' ')                                       , Sys.CLZ_HELP_PARAM)
        Sys.print(' '*50+'specified decrypted output filename'               , Sys.CLZ_HELP_ARG_INFO)

        Sys.dprint('\n')


    def print_help(self):
        """"""
        self.print_header()
        Sys.print(conf.PRG_DESC, Sys.CLZ_HELP_DESC)
        self.print_usage('',True)
        self.print_options()
        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.dprint()
        Sys.print('  EXEMPLES :\n', Sys.CLZ_HELP_CMD)
        CHQ  = "'"

        Sys.print(' '*4+'command key :', Sys.CLZ_HELP_CMD)

        Sys.print(' '*8+'# generate a new crypted key of 2048 length', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('key -l ', Sys.CLZ_HELP_CMD, False)
        Sys.print('2048 ', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# generate a new crypted key (default length is 1024) in a specified location', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('key -o ', Sys.CLZ_HELP_CMD, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM)


        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command encrypt :', Sys.CLZ_HELP_CMD)

        Sys.print(' '*8+'# encrypt specified file with default crypted key and default options', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.print(self.HOME+'mySecretTextFile.txt', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# encrypt specified file with specified crypted key (full compression, no random but mix mode)', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+'# on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.print('mySecretTextFile.txt', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -aRm -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('test.kmh', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# encrypt specified file with default crypted key (no compression but random & mix mode and multiprocessing)', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('enc ', Sys.CLZ_HELP_CMD, False)
        Sys.print('myBigTextFile.txt', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -Zrm -j ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('4', Sys.CLZ_HELP_PARAM)


        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command decrypt :', Sys.CLZ_HELP_CMD)

        Sys.print(' '*8+'# decrypt specified file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.print(self.HOME+'mySecretFile.kmh', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# decrypt specified file with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.print('myEncryptedSecretFile.kmh', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.print(self.HOME+'.kirmah'+Sys.sep+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('myDecryptedSecretFile.txt', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# decrypt specified file with default crypted key and multiprocessing', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('dec ', Sys.CLZ_HELP_CMD, False)
        Sys.print('myEncryptedSecretFile.kmh', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -j ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('4'    , Sys.CLZ_HELP_PARAM)


        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command split :', Sys.CLZ_HELP_CMD)

        Sys.print(' '*8+'# split specified file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('split ', Sys.CLZ_HELP_CMD, False)
        Sys.print(self.HOME+'myBigBinaryFile.avi', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# split specified file on 55 parts with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('split ', Sys.CLZ_HELP_CMD, False)
        Sys.print('myBigBinaryFile.avi', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -p ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('55'   , Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('myBigBinaryFile.encrypted', Sys.CLZ_HELP_PARAM)


        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.print('\n'+' '*4+'command merge :', Sys.CLZ_HELP_CMD)

        Sys.print(' '*8+'# merge specified splitted file with default crypted key', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('merge ', Sys.CLZ_HELP_CMD, False)
        Sys.print(self.HOME+'6136bd1b53d84ecbad5380594eea7256176c19e0266c723ea2e982f8ca49922b.kcf', Sys.CLZ_HELP_PARAM)

        Sys.print(' '*8+'# merge specified tark splitted file with specified crypted key on specified output location', Sys.CLZ_HELP_COMMENT)
        Sys.print(' '*8+conf.PRG_CLI_NAME+' ', Sys.CLZ_HELP_PRG, False)
        Sys.print('merge ', Sys.CLZ_HELP_CMD, False)
        Sys.print('myBigBinaryFile.encrypted.tark', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -k ' , Sys.CLZ_HELP_ARG, False)
        Sys.print(self.DIRKEY+'.myNewKey', Sys.CLZ_HELP_PARAM, False)
        Sys.print(' -o ' , Sys.CLZ_HELP_ARG, False)
        Sys.print('myBigBinaryFile.decrypted.avi', Sys.CLZ_HELP_PARAM)

        printLineSep(Const.LINE_SEP_CHAR,Const.LINE_SEP_LEN)
        Sys.dprint()
