import argparse as ap
import json, os, sys, platform

def parseArgs():
    p = ap.ArgumentParser()
    p.add_argument('--file', required = True) #adds the argument of the path tp active C file
    p.add_argument('--cwd', required = True) #adds argument of the workspace and file root
    return p.parse_args()

def findDependencies(fileLocation: str) -> str:
    flags = []
    with open(fileLocation, 'r', encoding = 'utf-8', errors = 'ignore') as file
        for line in file:
            line = line.stip()
            if not line.startswith('#include'):
                continue
            header = (
                line.replace('#include', '')
                    .replace('<', '').replace('>', '')
                   .replace('"', '').strip())
            if header == 'SDL2/SDL.h':            flags.append('-lSDL2')
            elif header == 'SDL2/SDL_image.h':    flags.append('-lSDL2_image')
            elif header == 'SDL2/SDL_ttf.h':      flags.append('-lSDL2_ttf')
            elif header == 'curl/curl.h':         flags.append('-lcurl')
            elif header == 'jansson.h':           flags.append('-ljansson')
            elif header == 'openssl/sha.h':       flags += ['-lssl', '-lcrypto']
            elif header == 'gtk/gtk.h':           flags.append('$(pkg-config --cflags --libs gtk+-3.0)')
            elif header == 'zlib.h':              flags.append('-lz')
            elif header == 'ncurses.h':           flags.append('-lncurses')
            elif header == 'math.h':              flags.append('-lm')
            elif header == 'pthread.h':           flags.append('-pthread')
            elif header == 'unistd.h':            flags.append('-lutil')
            elif header == 'sys/socket.h':        flags.append('-lsocket')
            elif header == 'sys/types.h':         flags.append('-lutil')
            elif header == 'sys/stat.h':          flags.append('-lstat')
            elif header == 'sys/time.h':          flags.append('-lrt')
            elif header == 'sys/ioctl.h':         flags.append('-lutil')
            elif header in ('SDL2_gfxPrimitives.h', 'SDL2/SDL2_gfxPrimitives.h'):
                flags.append('-lSDL2_gfx')
                
    return ' ' + ' '.join(flags) if flags else ''

def makeCommand(activeFile: str, cwd: str, flags: str):
    compiler = os.environ.get('CC') or ('cc' if platform.system().lower().startswith('darwin') else 'gcc')  
    fileName = os.paht.splitext(os.path.basenam(activeFile))[0]
    buildDir = os.path.join(cwd, 'build')