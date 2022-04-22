# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The copyright for song <Still Alive> belongs to Jonathan Coulton and Valve Software
# Contact me if there's copyright violation and if deletion of the content is needed.
#
#
#
# PORTAL--STILL ALIVE demo by LHF (BD4SUP)
# September 2021
# Runs with Python 3 on most terminals with an 80x24 characters area.
# This program was adjusted specifically for serial terminal under Linux
# (in this case, an Informer 213 @ 19200bps and Ubuntu 14.04)
# Feel free to do whatever you like with this code.
# Personnel credits come from this project: https://github.com/xBytez/aperturescience
# ASCII arts come from this project: https://sites.google.com/site/gaddc11/Stillalive.rar?attredirects=0&d=1
# My blog: EE Archeology @ http://7400.me


import time
import sys
import threading
import os
import shutil
import re
import signal
from pathlib import Path

cursor_x = 1
cursor_y = 1
print_lock = threading.Lock()


term = os.getenv("TERM", "vt100")
is_vt = re.search(r"vt(\d+)", term)

# xterm, rxvt, konsole ...
# but fbcon in linux kernel does not support screen buffer
enable_screen_buffer = not (is_vt or term == "linux")

# color support is after VT241
enable_color = not is_vt or int(re.search(r"\d+", is_vt.group()).group()) >= 241

enable_sound = '--no-sound' not in sys.argv

if enable_sound:
    import playsound

term_columns, term_lines = 0, 0
if is_vt:
    term_columns, term_lines = 80, 24
else:
    term_columns, term_lines = shutil.get_terminal_size()

term_columns = int(os.getenv("COLUMNS", term_columns))
term_lines = int(os.getenv("LINES", term_lines))

if term_columns < 80 or term_lines < 24:
    print("the terminal size should be at least 80x24")
    sys.exit(1)

is_draw_end = False

def sigint_handler(sig, frame):
    end_draw()
    print('Interrupt by user')
    sys.exit(0)

signal.signal(signal.SIGINT, sigint_handler)

def begin_draw():
    if enable_screen_buffer:
        print_lock.acquire()
        print('\033[?1049h', end='')
        print_lock.release()
    if enable_color:
        print_lock.acquire()
        print('\033[33;40;1m', end='')
        print_lock.release()


def end_draw():
    global is_draw_end
    print_lock.acquire()
    is_draw_end = True
    if enable_color:
        print('\033[0m', end='')
    if enable_screen_buffer:
        print('\033[?1049l', end='')
    else:
        clear(False)
        move(1, 1, False, False)
    print_lock.release()

def move(x, y, update_cursor=True, mutex=True):
    global cursor_x, cursor_y
    global print_lock
    if(mutex):
        print_lock.acquire()
    print("\033[%d;%dH" % (y, x), end='')
    sys.stdout.flush()
    if(update_cursor):
        cursor_x = x
        cursor_y = y
    if(mutex):
        print_lock.release()


def clear(mutex=True):
    global cursor_x, cursor_y
    global print_lock
    cursor_x = 1
    cursor_y = 1
    if mutex:
        print_lock.acquire()
    print('\033[2J', end='')
    if mutex:
        print_lock.release()

# print with mutex lock and cursor update. Use this for convenience


def _print(str, newline=True):
    global cursor_x, cursor_y
    global print_lock
    print_lock.acquire()
    if(newline):
        print(str)
        cursor_x = 1
        cursor_y = cursor_y + 1
    else:
        print(str, end='')
        cursor_x = cursor_x + len(str)
    print_lock.release()


class lyric:
    def __init__(self, _words, _time, _interval, _mode):
        '''
        Interval: -1 means to calculate based on last  
        Mode:   0: Lyric with new line
                1: Lyric without new line
                2: ASCII art
                3: Clear lyrics
                4: Start music
                5: Start credits
                9: END
        '''
        self.words = _words
        self.time = _time
        self.interval = _interval
        self.mode = _mode


ascii_art_width = 40
ascii_art_height = 20

credits_width = min((term_columns - 4) // 2, 56)
credits_height = term_lines - ascii_art_height - 2

lyric_width = term_columns - 4 - credits_width
lyric_height = term_lines - 2

credits_pos_x = lyric_width + 4

ascii_art_x = lyric_width + 4 + (credits_width - ascii_art_width) // 2
ascii_art_y = credits_height + 3

a1 = ["              .,-:;//;:=,               ",
      "          . :H@@@MM@M#H/.,+%;,          ",
      "       ,/X+ +M@@M@MM%=,-%HMMM@X/,       ",
      "     -+@MM; #M@@MH+-,;XMMMM@MMMM@+-     ",
      "    ;@M@@M- XM@X;. -+XXXXXHHH@M@M#@/.   ",
      "  ,%MM@@MH ,@%=            .---=-=:=,.  ",
      "  =@#@@@MX .,              -%HX##%%%+;  ",
      " =-./@M@M$                  .;@MMMM@MM: ",
      " X@/ -#MM/                    .+MM@@@M$ ",
      ",@M@H: :@:                    . =X#@@@@-",
      ",@@@MMX, .                    /H- ;@M@M=",
      ".H@@@@M@+,                    %MM+..%#$.",
      " /MMMM@MMH/.                  XM@MH; =; ",
      "  /%+%#XHH@$=              , .H@@@@MX,  ",
      "   .=--------.           -%H.,@@@@@MX,  ",
      "   .%MM@@@HHHXX###%+= .:#MMX =M@@MM%.   ",
      "     =XMMM@MM@MM#H;,-+HMM@M+ /MMMX=     ",
      "       =%@M@M#@$-.=#@MM@@@M; %M%=       ",
      "         ,:+$+-,/H#MMMMMMM@= =,         ",
      "               =++%%%%+/:-.             "]

a2 = ["             =+$HM####@H%;,             ",
      "          /H###############M$,          ",
      "          ,@################+           ",
      "           .H##############+            ",
      "             X############/             ",
      "              $##########/              ",
      "               %########/               ",
      "                /X/;;+X/                ",
      "                 -XHHX-                 ",
      "                ,######,                ",
      "#############X  .M####M.  X#############",
      "##############-   -//-   -##############",
      "X##############%,      ,+##############X",
      "-##############X        X##############-",
      " %############%          %############% ",
      "  %##########;            ;##########%  ",
      "   ;#######M=              =M#######;   ",
      "    .+M###@,                ,@###M+.    ",
      "       :XH.                  .HX:       ",
      "                                        "]

a3 = ["                 =/;;/-                 ",
      "                +:    //                ",
      "               /;      /;               ",
      "              -X        H.              ",
      ".//;;;:;;-,   X=        :+   .-;:=;:;%;.",
      "M-       ,=;;;#:,      ,:#;;:=,       ,@",
      ":%           :%.=/++++/=.$=           %=",
      " ,%;         %/:+/;,,/++:+/         ;+. ",
      "   ,+/.    ,;@+,        ,%H;,    ,/+,   ",
      "      ;+;;/= @.  .H##X   -X :///+;      ",
      "      ;+=;;;.@,  .XM@$.  =X.//;=%/.     ",
      "   ,;:      :@%=        =$H:     .+%-   ",
      " ,%=         %;-///==///-//         =%, ",
      ";+           :%-;;;:;;;;-X-           +:",
      "@-      .-;;;;M-        =M/;;;-.      -X",
      " :;;::;;-.    %-        :+    ,-;;-;:== ",
      "              ,X        H.              ",
      "               ;/      %=               ",
      "                //    +;                ",
      "                 ,////,                 "]

a4 = ["                          .,---.        ",
      "                        ,/XM#MMMX;,     ",
      "                      -%##########M%,   ",
      "                     -@######%  $###@=  ",
      "      .,--,         -H#######$   $###M: ",
      "   ,;$M###MMX;     .;##########$;HM###X=",
      " ,/@##########H=      ;################+",
      "-+#############M/,      %##############+",
      "%M###############=      /##############:",
      "H################      .M#############;.",
      "@###############M      ,@###########M:. ",
      "X################,      -$=X#######@:   ",
      "/@##################%-     +######$-    ",
      ".;##################X     .X#####+,     ",
      " .;H################/     -X####+.      ",
      "   ,;X##############,       .MM/        ",
      "      ,:+$H@M#######M#$-    .$$=        ",
      "           .,-=;+$@###X:    ;/=.        ",
      "                  .,/X$;   .::,         ",
      "                      .,    ..          "]

a5 = ["            .+                          ",
      "             /M;                        ",
      "              H#@:              ;,      ",
      "              -###H-          -@/       ",
      "               %####$.  -;  .%#X        ",
      "                M#####+;#H :M#M.        ",
      "..          .+/;%#########X###-         ",
      " -/%H%+;-,    +##############/          ",
      "    .:$M###MH$%+############X  ,--=;-   ",
      "        -/H#####################H+=.    ",
      "           .+#################X.        ",
      "         =%M####################H;.     ",
      "            /@###############+;;/%%;,   ",
      "         -%###################$.        ",
      "       ;H######################M=       ",
      "    ,%#####MH$%;+#####M###-/@####%      ",
      "  :$H%+;=-      -####X.,H#   -+M##@-    ",
      " .              ,###;    ;      =$##+   ",
      "                .#H,               :XH, ",
      "                 +                   .;-"]

a6 = ["                     -$-                ",
      "                    .H##H,              ",
      "                   +######+             ",
      "                .+#########H.           ",
      "              -$############@.          ",
      "            =H###############@  -X:     ",
      "          .$##################:  @#@-   ",
      "     ,;  .M###################;  H###;  ",
      "   ;@#:  @###################@  ,#####: ",
      " -M###.  M#################@.  ;######H ",
      " M####-  +###############$   =@#######X ",
      " H####$   -M###########+   :#########M, ",
      "  /####X-   =########%   :M########@/.  ",
      "    ,;%H@X;   .$###X   :##MM@%+;:-      ",
      "                 ..                     ",
      "  -/;:-,.              ,,-==+M########H ",
      " -##################@HX%%+%%$%%%+:,,    ",
      "   .-/H%%%+%%$H@###############M@+=:/+: ",
      "/XHX%:#####MH%=    ,---:;;;;/%%XHM,:###$",
      "$@#MX %+;-                           .  "]

a7 = ["                                     :X-",
      "                                  :X### ",
      "                                ;@####@ ",
      "                              ;M######X ",
      "                            -@########$ ",
      "                          .$##########@ ",
      "                         =M############-",
      "                        +##############$",
      "                      .H############$=. ",
      "         ,/:         ,M##########M;.    ",
      "      -+@###;       =##########M;       ",
      "   =%M#######;     :#########M/         ",
      "-$M###########;   :#########/           ",
      " ,;X###########; =########$.            ",
      "     ;H#########+#######M=              ",
      "       ,+##############+                ",
      "          /M#########@-                 ",
      "            ;M######%                   ",
      "              +####:                    ",
      "               ,$M-                     "]

a8 = ["           .-;+$XHHHHHHX$+;-.           ",
      "        ,;X@@X%/;=----=:/%X@@X/,        ",
      "      =$@@%=.              .=+H@X:      ",
      "    -XMX:                      =XMX=    ",
      "   /@@:                          =H@+   ",
      "  %@X,                            .$@$  ",
      " +@X.                               $@% ",
      "-@@,                                .@@=",
      "%@%                                  +@$",
      "H@:                                  :@H",
      "H@:         :HHHHHHHHHHHHHHHHHHX,    =@H",
      "%@%         ;@M@@@@@@@@@@@@@@@@@H-   +@$",
      "=@@,        :@@@@@@@@@@@@@@@@@@@@@= .@@:",
      " +@X        :@@@@@@@@@@@@@@@M@@@@@@:%@% ",
      "  $@$,      ;@@@@@@@@@@@@@@@@@M@@@@@@$. ",
      "   +@@HHHHHHH@@@@@@@@@@@@@@@@@@@@@@@+   ",
      "    =X@@@@@@@@@@@@@@@@@@@@@@@@@@@@X=    ",
      "      :$@@@@@@@@@@@@@@@@@@@M@@@@$:      ",
      "        ,;$@@@@@@@@@@@@@@@@@@X/-        ",
      "           .-;+$XXHHHHHX$+;-.           "]

a9 = ["            ,:/+/-                      ",
      "            /M/              .,-=;//;-  ",
      "       .:/= ;MH/,    ,=/+%$XH@MM#@:     ",
      "      -$##@+$###@H@MMM#######H:.    -/H#",
      " .,H@H@ X######@ -H#####@+-     -+H###@ ",
      "  .,@##H;      +XM##M/,     =%@###@X;-  ",
      "X%-  :M##########$.    .:%M###@%:       ",
      "M##H,   +H@@@$/-.  ,;$M###@%,          -",
      "M####M=,,---,.-%%H####M$:          ,+@##",
      "@##################@/.         :%H##@$- ",
      "M###############H,         ;HM##M$=     ",
      "#################.    .=$M##M$=         ",
      "################H..;XM##M$=          .:+",
      "M###################@%=           =+@MH%",
      "@################M/.          =+H#X%=   ",
      "=+M##############M,       -/X#X+;.      ",
      "  .;XM##########H=    ,/X#H+:,          ",
      "     .=+HM######M+/+HM@+=.              ",
      "         ,:/%XM####H/.                  ",
      "              ,.:=-.                    "]

a10 = ["       #+ @      # #              M#@   ",
       " .    .X  X.%##@;# #   +@#######X. @#%  ",
       "   ,==.   ,######M+  -#####%M####M-    #",
       "  :H##M%:=##+ .M##M,;#####/+#######% ,M#",
       " .M########=  =@#@.=#####M=M#######=  X#",
       " :@@MMM##M.  -##M.,#######M#######. =  M",
       "             @##..###:.    .H####. @@ X,",
       "   ############: ###,/####;  /##= @#. M ",
       "           ,M## ;##,@#M;/M#M  @# X#% X# ",
       ".%=   ######M## ##.M#:   ./#M ,M #M ,#$ ",
       "##/         $## #+;#: #### ;#/ M M- @# :",
       "#+ #M@MM###M-;M #:$#-##$H# .#X @ + $#. #",
       "      ######/.: #%=# M#:MM./#.-#  @#: H#",
       "+,.=   @###: /@ %#,@  ##@X #,-#@.##% .@#",
       "#####+;/##/ @##  @#,+       /#M    . X, ",
       "   ;###M#@ M###H .#M-     ,##M  ;@@; ###",
       "   .M#M##H ;####X ,@#######M/ -M###$  -H",
       "    .M###%  X####H  .@@MM@;  ;@#M@      ",
       "      H#M    /@####/      ,++.  / ==-,  ",
       "               ,=/:, .+X@MMH@#H  #####$="]

ascii_art = [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10]

# Timestamps are adjusted according to actual situations...
# For Informer213 running at 19200bps, refreshing a ASCII art pattern
# takes ~600ms, so we add 700ms between every pattern and the next line

lyrics = [
    ##########  Page 1  ##########
    lyric("Forms FORM-29827281-12:",            0,      -1,   0),
    lyric("Test Assessment Report",             200,    -1,   0),
    lyric("\00\00\00\00\00\00\00",              400,    - \
          1,   0),  # Keep flushing the buffer
    lyric("",                                   710,    0,    4),  # Music start
    lyric("This was a triumph.",                730,    2,    0),
    lyric("",                                   930,    0,    5),  # Credits start
    lyric("I'm making a note here:",            1123,   2,    0),
    lyric("HUGE SUCCESS.",                      1347,   1.7,  0),
    lyric("It's hard to overstate",             1627,   -1,   0),
    lyric("my satisfaction.",                   1873,   2.6,  0),
    lyric("Aperture Science",                   2350,   1.8,  0),
    lyric(0,                                    2350,   0,    2),  # ASCII 1
    lyric("We do what we must",                 2733,   1.6,  0),
    lyric("because we can.",                    2910,   1.5,  0),
    lyric("For the good of all of us.",         3237,   -1,   0),
    lyric(1,                                    3500,   0,    2),  # ASCII 2
    lyric("Except the ones who are dead.",      3567,   -1,   0),
    lyric("",                                   3717,   0.05, 0),
    lyric(0,                                    3717,   0,    2),  # ASCII 1
    lyric("But there's no sense crying",        3787,   -1,   0),
    lyric("over every mistake.",                3973,   1.77, 0),
    lyric("You just keep on trying",            4170,   -1,   0),
    lyric("till you run out of cake.",          4370,   -1,   0),
    lyric(2,                                    4500,   0,    2),  # ASCII 3
    lyric("And the Science gets done.",         4570,   -1,   0),
    lyric("And you make a neat gun.",           4767,   -1,   0),
    lyric(0,                                    4903,   0,    2),  # ASCII 1
    lyric("For the people who are",             4973,   -1,   0),
    lyric("still alive.",                       5110,   1.6,  1),

    ##########  Page 2  ##########
    lyric(0,                                    5353,
          0,    3),  # Clear lyrics
    lyric("Forms FORM-55551-5:",                5413,   -1,   0),
    lyric("Personnel File Addendum:",           5477,   1.13, 0),
    lyric("",                                   5650,   0.05, 0),
    lyric("Dear <<Subject Name Here>>,",        5650,   -1,   0),
    lyric("",                                   5900,   -1,   0),
    lyric("I'm not even angry.",                5900,   1.86, 0),
    lyric("I'm being ",                         6320,   -1,   1),
    lyric("so ",                                6413,   -1,   1),
    lyric("sincere right now.",                 6470,   1.9,  0),
    lyric("Even though you broke ",             6827,   -1,   1),
    lyric(3,                                    7020,   0,    2),  # ASCII 4
    lyric("my heart.",                          7090,   -1,   0),
    lyric("And killed me.",                     7170,   1.43, 0),
    lyric(4,                                    7300,   0,    2),  # ASCII 5
    lyric("And tore me to pieces.",             7500,   1.83, 0),
    lyric("And threw every piece ",             7900,   -1,   1),
    lyric("into a fire.",                       8080,   1.8,  0),
    lyric(5,                                    8080,   0,    2),  # ASCII 6
    lyric("As they burned it hurt because",     8430,   -1,   0),
    lyric(6,                                    8690,   0,    2),  # ASCII 7
    lyric("I was so happy for you!",            8760,   1.67, 0),
    lyric("Now, these points of data",          8960,   -1,   0),
    lyric("make a beautiful line.",             9167,   -1,   0),
    lyric("And we're out of beta.",             9357,   -1,   0),
    lyric("We're releasing on time.",           9560,   -1,   0),
    lyric(4,                                    9700,   0,    2),  # ASCII 5
    lyric("So I'm GLaD. I got burned.",          9770,   -1,   0),
    lyric(2,                                    9913,   0,    2),  # ASCII 3
    lyric("Think of all the things we learned", 9983,   -1,   0),
    lyric(0,                                    10120,  0,    2),  # ASCII 1
    lyric("for the people who are",             10190,  -1,   0),
    lyric("still alive.",                       10327,  1.8,  0),

    ##########  Page 3  ##########
    lyric(0,                                    10603,
          0,    3),  # Clear lyrics
    lyric("Forms FORM-55551-6:",                10663,  -1,   0),
    lyric("Personnel File Addendum Addendum:",  10710,  1.36, 0),
    lyric("",                                   10710,  0.05, 0),
    lyric("One last thing:",                    10910,  -1,   0),
    lyric("",                                   11130,  0.05, 0),
    lyric("Go ahead and leave ",                11130,  -1,   1),
    lyric("me.",                                11280,  0.5,  0),
    lyric("I think I prefer to stay ",        11507,  -1,   1),
    lyric("inside.",                            11787,  1.13, 0),
    lyric("Maybe you'll find someone else",     12037,  -1,   0),
    lyric("to help you.",                       12390,  1.23, 0),
    lyric("Maybe Black ",                       12737,  -1,   1),
    lyric(7,                                    12787,  0,    2),  # ASCII 8
    lyric("Mesa...",                            12857,  2.7,  0),
    lyric("THAT WAS A JOKE.",                   13137,  1.46, 1),
    lyric(" FAT CHANCE.",                       13387,  1.1,  0),
    lyric("Anyway, ",                           13620,  -1,   1),
    lyric(8,                                    13670,  0,    2),  # ASCII 9
    lyric("this cake is great.",                13740,  -1,   0),
    lyric("It's so delicious and moist.",       13963,  -1,   0),
    lyric(9,                                    14123,  0,    2),  # ASCII 10
    lyric("Look at me still talking",           14193,  -1,   0),
    lyric(1,                                    14320,  0,    2),  # ASCII 2
    lyric("when there's Science to do.",        14390,  -1,  0),
    lyric(0,                                    14527,  0,    2),  # ASCII 1
    lyric("When I look out there,",             14597,  -1,   0),
    lyric("it makes me GLaD I'm not you.",      14767,  -1,   0),
    lyric(2,                                    14913,  0,    2),  # ASCII 3
    lyric("I've experiments to run.",           14983,  -1,   0),
    lyric(4,                                    15120,  0,    2),  # ASCII 5
    lyric("There is research to be done.",      15190,  -1,   0),
    lyric(0,                                    15320,  0,    2),  # ASCII 1
    lyric("On the people who are",              15390,  -1,   0),
    lyric("still alive",                        15553,  2.0,  1),

    ##########  Page 4  ##########
    lyric(0,                                    15697,
          0,    3),  # Clear lyrics
    lyric("",                                   15757,  0.05, 0),
    lyric("",                                   15757,  0.05, 0),
    lyric("",                                   15757,  0.05, 0),
    lyric("PS: And believe me I am",            15757,  -1,   0),
    lyric("still alive.",                       15960,  1.13, 0),
    lyric("PPS: I'm doing Science and I'm",     16150,  -1,   0),
    lyric("still alive.",                       16363,  1.13, 0),
    lyric("PPPS: I feel FANTASTIC and I'm",     16550,  -1,   0),
    lyric("still alive.",                       16760,  -1,   0),
    lyric("",                                   16860,  -1,   0),
    lyric("FINAL THOUGHT:",                      16860,  -1,   0),
    lyric("While you're dying I'll be",         16993,  -1,   0),
    lyric("still alive.",                       17157,  -1,   0),
    lyric("",                                   17277,  -1,   0),
    lyric("FINAL THOUGHT PS:",                   17277,  -1,   0),
    lyric("And when you're dead I will be",     17367,  -1,   0),
    lyric("still alive.",                       17550,  1.13, 0),
    lyric("",                                   17550,  -1,   0),
    lyric("",                                   17550,  0.05, 0),
    lyric("STILL ALIVE",                        17760,  1.13, 0),
    lyric(0,                                    17900,
          0,    3),  # Clear lyrics
    lyric(0,                                    18500,
          0,    3),  # Clear lyrics
    lyric("ENDENDENDENDENDENDENDEND",           18500,  0.05, 9)]

credits = r""">LIST PERSONNEL
            
Gautam Babbar
Ted Backman
Kelly Bailey
Jeff Ballinger
Aaron Barber
Jeep Barnett
Jeremy Bennett
Dan Berger
Yahn Bernier
Ken Birdwell
Derrick BirumMike Blaszczak
Iestyn Bleasdale-Shepherd
Chris Bokitch
Steve Bond
Matt Boone
Antoine Bourdon
Jamaal Bradley
Jason Brashill
Charlie Brown
Charlie Burgin
Andrew Burke
Augusta Butlin
Julie Caldwell
Dario Casali
Chris Chin
Jess Cliffe
Phil Co
John Cook
Christen Coomer
Greg Coomer
Scott Dalton
Kerry Davis
Jason Deakins
Joe Demers
Ariel Diaz
Quintin Doroquez
Jim Dose
Chris Douglass
Laura Dubuk
Mike Dunkle
Mike Durand
Mike Dussault
Dhabih Eng
Katie Engel
Chet Faliszek
Adrian Finol
Bill Fletcher
Moby Francke
Stephane Gaudette
Kathy Gehrig
Vitaliy Genkin
Paul Graham
Chris Green
Chris Grinstead
John Guthrie
Aaron Halifax
Reagan Halifax
Leslie Hall
Jeff Hameluck
Joe Han
Don Holden
Jason Holtman
Gray Horsfield
Keith Huggins
Jim Hughes
Jon Huisingh
Brian Jacobson
Lars Jensvold
Erik Johnson
Jakob Jungels
Rich Kaethler
Steve Kalning
Aaron Kearly
Iikka Keranen
David Kircher
Eric Kirchmer
Scott Klintworth
Alden Kroll
Marc Laidlaw
Jeff Lane
Tim Larkin
Dan LeFree
Isabelle LeMay
Tom Leonard
Jeff Lind
Doug Lombardi
Bianca Loomis
Richard Lord
Realm Lovejoy
Randy Lundeen
Scott Lynch
Ido Magal
Nick Maggiore
John McCaskey
Patrick McClard
Steve McClure
Hamish McKenzie
Gary McTaggart
Jason Mitchell
Mike Morasky
John Morello II
Bryn Moslow
Arsenio Navarro
Gabe Newell
Milton Ngan
Jake Nicholson
Martin Otten
Nick Papineau
Karen Prell
Bay Raitt
Tristan Reidford
Alfred Reynolds
Matt Rhoten
Garret Rickey
Dave Riller
Elan Ruskin
Matthew Russell
Jason Ruymen
David Sawyer
Marc Scaparro
Wade Schin
Matthew Scott
Aaron Seeler
Jennifer Seeley
Taylor Sherman
Eric Smith
Jeff Sorensen
David Speyrer
Jay Stelly
Jeremy Stone
Eric Strand
Kim Swift
Kelly Thornton
Eric Twelker
Carl Uhlman
Doug Valente
Bill Van Buren
Gabe Van Engel
Alex Vlachos
Robin Walker
Joshua Weier
Andrea Wicklund
Greg Winkler
Erik Wolpaw
Doug Wood
Matt T. Wood
Danika Wright
Matt Wright
Shawn Zabecki
Torsten Zabka 
            
            
'Still Alive' by:
Jonathan Coulton
            
Voices:
Ellen McLain - GlaDOS, Turrets
Mike Patton - THE ANGER SPHERE
            
Voice Casting:
Shana Landsburg\Teri Fiddleman
            
Voice Recording:
Pure Audio, Seattle, WA
            
Voice recording
scheduling and logistics:
Pat Cockburn, Pure Audio
            
Translations:
SDL
            
Crack Legal Team:
Liam Lavery
Karl Quackenbush
Kristen Boraas
Kevin Rosenfield
Alan Bruggeman
Dennis Tessier
            
Thanks for the use of their face:
Alesia Glidewell - Chell
            
Special thanks to everyone at:
Alienware
ATI
Dell
Falcon Northwest
Havok
SOFTIMAGE
and Don Kemmis, SLK Technologies
            
            
THANK YOU FOR PARTICIPATING
IN THIS
ENRICHMENT CENTER ACTIVITY!!"""


def drawAA(x, y, ch):
    for dy in range(ascii_art_height):
        move(x, y + dy)
        print(ascii_art[ch][dy], end='')
        sys.stdout.flush()
        time.sleep(0.01)


def drawFrame():
    move(1, 1)
    _print(' ' + '-' * lyric_width + '  ' + '-' * credits_width + ' ', not is_vt)
    for _ in range(credits_height):
        _print('|' + ' ' * lyric_width + '||' + ' ' * credits_width + '|', not is_vt)
    _print('|' + ' ' * lyric_width + '| ' + '-' * credits_width + ' ', not is_vt)
    for _ in range(lyric_height - 1 - credits_height):
        _print('|' + ' ' * lyric_width + '|')
    _print(' ' + '-' * lyric_width + ' ', False)
    move(2, 2)
    sys.stdout.flush()
    time.sleep(1)


def clearLyrics():
    move(1, 2)
    for _ in range(lyric_height):
        _print('|' + ' ' * lyric_width)
    move(2, 2)


def drawLyrics(str, x, y, interval, newline):
    move(x + 2, y + 2)
    for ch in str:
        _print(ch, False)
        sys.stdout.flush()
        time.sleep(interval)
        x = x + 1
    if(newline):
        x = 0
        y = y + 1
        move(x + 2, y + 2)
    return x


class thread_credits (threading.Thread):
    def run(self):
        global print_lock
        global cursor_x, cursor_y
        credit_x = 0
        i = 0
        length = len(credits)
        last_credits = [""]
        startTime = time.time()
        for ch in credits:
            currentTime = startTime + 174.0 / length * i
            i += 1
            if ch == '\n':
                credit_x = 0
                last_credits.append("")
                if len(last_credits) > credits_height:
                    last_credits = last_credits[-credits_height:]
                print_lock.acquire()
                if is_draw_end:
                    print_lock.release()
                    break
                for y in range(2, 2 + credits_height - len(last_credits)):
                    move(credits_pos_x, y, False, False)
                    print(' ' * credits_width, end='')
                for k in range(len(last_credits)):
                    y = 2 + credits_height - len(last_credits) + k
                    move(credits_pos_x, y, False, False)
                    print(last_credits[k], end='')
                    print(' ' * (credits_width - len(last_credits[k])), end='')
                move(cursor_x, cursor_y, False, False)
                print_lock.release()
            else:
                last_credits[-1] += ch
                print_lock.acquire()
                if is_draw_end:
                    print_lock.release()
                    break
                move(credits_pos_x + credit_x, credits_height + 1, False, False)
                print(ch, end='')
                move(cursor_x, cursor_y, False, False)
                print_lock.release()
                credit_x += 1
            while time.time() < currentTime:
                time.sleep(0.01)


################# Main ################
begin_draw()
clear()
drawFrame()
move(2, 2)
time.sleep(1)

startTime = time.time() * 100
currentTime = 0
currentLyric = 0
currentCredit = 0
x = 0
y = 0

while(lyrics[currentLyric].mode != 9):
    currentTime = time.time() * 100 - startTime

    if(currentTime > lyrics[currentLyric].time):

        if(lyrics[currentLyric].mode <= 1 or lyrics[currentLyric].mode >= 5):
            wordCount = len(lyrics[currentLyric].words)
        if(wordCount == 0):
            wordCount = 1

        if(lyrics[currentLyric].interval < 0):
            interval = (lyrics[currentLyric + 1].time -
                        lyrics[currentLyric].time) / 100.0 / wordCount
        else:
            interval = lyrics[currentLyric].interval / wordCount

        if(lyrics[currentLyric].mode == 0):
            x = drawLyrics(lyrics[currentLyric].words,
                           x, y,
                           interval,
                           True)
            y = y + 1
        elif(lyrics[currentLyric].mode == 1):
            x = drawLyrics(lyrics[currentLyric].words,
                           x, y,
                           interval,
                           False)
        elif(lyrics[currentLyric].mode == 2):
            drawAA(ascii_art_x, ascii_art_y, lyrics[currentLyric].words)
            move(x + 2, y + 2)
        elif(lyrics[currentLyric].mode == 3):
            clearLyrics()
            x = 0
            y = 0
        elif(lyrics[currentLyric].mode == 4):
            if enable_sound:
                playsound.playsound(str(Path.cwd() / 'sa1.mp3'), False)
        elif(lyrics[currentLyric].mode == 5):
            th_credit = thread_credits()
            th_credit.daemon = True
            th_credit.start()
        currentLyric = currentLyric + 1

    time.sleep(0.01)

end_draw()
