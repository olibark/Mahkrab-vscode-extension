#!/usr/bin/env python3
import argparse as ap
import json, os, sys, platform
import shlex

def parseArgs():
    p = ap.ArgumentParser()
    p.add_argument('--file', required=True) #source file
    p.add_argument('--cwd',  required=True) #working directory (the root)
    return p.parse_args()

def findDependencies(fileLocation: str) -> str:
    flags = [] #holds the flags needed in source
    try:
        with open(fileLocation, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                if not line.startswith('#include'):
                    continue #ignoring non-include lines
                header = (
                    line.replace('#include', '')
                        .replace('<', '').replace('>', '')
                        .replace('"', '').strip() #extracts the file name of the header
                )
                
                """HEADER-LISTS"""
                if header == 'SDL2/SDL.h':            flags.append('-lSDL2')
                elif header == 'SDL2/SDL_image.h':    flags.append('-lSDL2_image')
                elif header == 'SDL2/SDL_ttf.h':      flags.append('-lSDL2_ttf')
                elif header in ('SDL2_gfxPrimitives.h', 'SDL2/SDL2_gfxPrimitives.h'): flags.append('-lSDL2_gfx')
                elif header == 'SDL2/SDL_mixer.h':    flags.append('-lSDL2_mixer')
                elif header == 'SDL2/SDL_net.h':      flags.append('-lSDL2_net')
                elif header == 'curl/curl.h':         flags.append('-lcurl')
                elif header == 'jansson.h':           flags.append('-ljansson')
                elif header in ('json-c/json.h',):    flags.append('-ljson-c')
                elif header in ('openssl/ssl.h',
                                 'openssl/sha.h',
                                 'openssl/evp.h'):    flags += ['-lssl', '-lcrypto']
                elif header == 'gtk/gtk.h':           flags.append('$(pkg-config --cflags --libs gtk+-3.0)')
                elif header == 'glib.h':              flags.append('$(pkg-config --cflags --libs glib-2.0)')
                elif header == 'gdk-pixbuf/gdk-pixbuf.h': flags.append('$(pkg-config --cflags --libs gdk-pixbuf-2.0)')
                elif header == 'pango/pango.h':       flags.append('$(pkg-config --cflags --libs pango)')
                elif header == 'zlib.h':              flags.append('-lz')
                elif header == 'bzlib.h':             flags.append('-lbz2')
                elif header == 'lz4.h':               flags.append('-llz4')
                elif header == 'archive.h':           flags.append('-larchive')
                elif header == 'ncurses.h':           flags.append('-lncurses')
                elif header in ('readline/readline.h',
                                 'readline/history.h'): flags.append('-lreadline')
                elif header == 'sqlite3.h':           flags.append('-lsqlite3')
                elif header == 'mysql/mysql.h':       flags.append('-lmysqlclient')
                elif header == 'mariadb/mysql.h':     flags.append('-lmariadb')
                elif header == 'pq-fe.h':             flags.append('-lpq')
                elif header == 'expat.h':             flags.append('-lexpat')
                elif header in ('libxml/parser.h',
                                 'libxml2/libxml/parser.h'): flags.append('-lxml2')
                elif header in ('yaml.h', 'libyaml/yaml.h'): flags.append('-lyaml')
                elif header == 'png.h':               flags.append('-lpng')
                elif header == 'jpeglib.h':           flags.append('-ljpeg')
                elif header == 'tiffio.h':            flags.append('-ltiff')
                elif header == 'portaudio.h':         flags.append('-lportaudio')
                elif header == 'alsa/asoundlib.h':    flags.append('-lasound')
                elif header == 'sndfile.h':           flags.append('-lsndfile')
                elif header == 'ao/ao.h':             flags.append('-lao')
                elif header == 'mpg123.h':            flags.append('-lmpg123')
                elif header == 'vorbis/vorbisfile.h': flags.append('-lvorbisfile')
                elif header == 'opus/opus.h':         flags.append('-lopus')
                elif header == 'FLAC/stream_decoder.h': flags.append('-lFLAC')
                elif header == 'fftw3.h':             flags.append('-lfftw3')
                elif header == 'lapacke.h':           flags.append('-llapacke')
                elif header == 'blas.h':              flags.append('-lblas')
                elif header == 'uv.h':                flags.append('-luv')
                elif header == 'event.h':             flags.append('-levent')
                elif header == 'pcap/pcap.h':         flags.append('-lpcap')
                elif header == 'uuid/uuid.h':         flags.append('-luuid')
                elif header == 'hidapi/hidapi.h':     flags.append('-lhidapi')
                elif header == 'bluetooth/bluetooth.h': flags.append('-lbluetooth')
                elif header == 'X11/Xlib.h':          flags.append('-lX11')
                elif header == 'png++/png.hpp':       flags.append('-lpng')
                elif header == 'math.h':              flags.append('-lm')
                elif header == 'pthread.h':           flags.append('-pthread')
    except FileNotFoundError:
        return ''
    return ' ' + ' '.join(flags) if flags else ''

def shlexSafety(cwd, buildDir, src, execPath):
    safeCwd = shlex.quote(cwd)
    safeBuildDir = shlex.quote(buildDir)
    safeSrc = shlex.quote(src)
    safeExe = shlex.quote(execPath)
    return safeCwd, safeBuildDir, safeSrc, safeExe

def makeCommand(activeFile: str, cwd: str, flags: str): #takes in the source/active file, the working directry, and the flags found in the dict
    compiler = os.environ.get('CC') or ('cc' if platform.system().lower().startswith('darwin') else 'gcc')
    fileName = os.path.splitext(os.path.basename(activeFile))[0]
    buildDir = os.path.join(cwd, 'build') #finds build directory
    executePath = os.path.join(buildDir, fileName) #where file is run from
    if platform.system().lower().startswith('win'): #checks if windows as exe is needed
        executePath += '.exe'
    safeCwd, safeBuildDir, safeSrc, safeExe = shlexSafety(cwd, buildDir, activeFile, executePath)
    compileCommand = f'{compiler} {safeSrc} -o {safeExe}{flags}' #links compiler, source, output, and flags together, compiling the program
    #Use a script block to swallow extra args in PowerShell
    runCommand = f'& {safeExe}' if platform.system().lower().startswith('win') else f'./{shlex.quote(os.path.relpath(executePath, cwd))}'
    is_powershell = 'pwsh' in os.environ.get('SHELL', '').lower() or 'powershell' in os.environ.get('COMSPEC', '').lower() or 'PSModulePath' in os.environ
    
    """checks OS and Shell for syntax differences"""
    
    if platform.system().lower().startswith('win'):#windows
        if is_powershell:
            mkdir_cmd = f"if (!(Test-Path {safeBuildDir})) {{ mkdir {safeBuildDir} }}"
            fullCommand = f"cd {safeCwd}; {mkdir_cmd}; {compileCommand}; {runCommand}"
        else:
            mkdir_cmd = f'if not exist {safeBuildDir} mkdir {safeBuildDir}'
            fullCommand = f'cd {safeCwd} && {mkdir_cmd} && {compileCommand} && {safeExe}'
    else: #unix
        mkdir_cmd = f'mkdir -p {safeBuildDir}'
        fullCommand = f'cd {safeCwd} && {mkdir_cmd} && {compileCommand} && {runCommand}'
    return compileCommand, runCommand, fullCommand

args = parseArgs()
activeFile = os.path.abspath(os.path.expanduser(args.file)) #finds the active file from the arguments passed to the script from extension.js
cwd = os.path.abspath(os.path.expanduser(args.cwd)) #finds working directory
if not os.path.exists(activeFile): #error handling
    print(f'ERROR: file not found: {activeFile}', file=sys.stderr); sys.exit(2)
if not os.path.isdir(cwd):
    print(f'ERROR: cwd not a directory: {cwd}', file=sys.stderr); sys.exit(2)
flags = findDependencies(activeFile)
compileCmd, runCmd, fullCmd = makeCommand(activeFile, cwd, flags)
print(json.dumps({"compile": compileCmd, "run": runCmd, "full": fullCmd}))
