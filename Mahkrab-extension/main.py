#!/usr/bin/env python3
import argparse as ap
import json, os, sys, platform
import shlex

def parseArgs():
    p = ap.ArgumentParser()
    p.add_argument('--file', required=True)  # path to active C file
    p.add_argument('--cwd',  required=True)  # workspace root
    return p.parse_args()

def findDependencies(fileLocation: str) -> str:
    flags = []
    try:
        with open(fileLocation, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                line = line.strip()
                if not line.startswith('#include'):
                    continue
                header = (
                    line.replace('#include', '')
                        .replace('<', '').replace('>', '')
                        .replace('"', '').strip()
                )
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
    except FileNotFoundError:
        return ''
    return ' ' + ' '.join(flags) if flags else ''

def shlexSafety(cwd, buildDir, src, execPath):
    safeCwd = shlex.quote(cwd)
    safeBuildDir = shlex.quote(buildDir)
    safeSrc = shlex.quote(src)
    safeExe = shlex.quote(execPath)
    return safeCwd, safeBuildDir, safeSrc, safeExe

def makeCommand(activeFile: str, cwd: str, flags: str):
    compiler = os.environ.get('CC') or ('cc' if platform.system().lower().startswith('darwin') else 'gcc')
    fileName = os.path.splitext(os.path.basename(activeFile))[0]
    buildDir = os.path.join(cwd, 'build')
    executePath = os.path.join(buildDir, fileName)

    if platform.system().lower().startswith('win'):
        executePath += '.exe'

    safeCwd, safeBuildDir, safeSrc, safeExe = shlexSafety(cwd, buildDir, activeFile, executePath)
    
    compileCommand = f'{compiler} {safeSrc} -o {safeExe}{flags}'
    runCommand = safeExe if platform.system().lower().startswith('win') \
        else f'./{shlex.quote(os.path.relpath(executePath, cwd))}'
    fullCommand = f'cd {safeCwd} && mkdir -p {safeBuildDir} && {compileCommand} && {runCommand}'
    return compileCommand, runCommand, fullCommand

if __name__ == '__main__':
    args = parseArgs()

    activeFile = os.path.abspath(os.path.expanduser(args.file))
    cwd = os.path.abspath(os.path.expanduser(args.cwd))

    if not os.path.exists(activeFile):
        print(f'ERROR: file not found: {activeFile}', file=sys.stderr); sys.exit(2)
    if not os.path.isdir(cwd):
        print(f'ERROR: cwd not a directory: {cwd}', file=sys.stderr); sys.exit(2)

    flags = findDependencies(activeFile)
    compileCmd, runCmd, fullCmd = makeCommand(activeFile, cwd, flags)

    print(json.dumps({"compile": compileCmd, "run": runCmd, "full": fullCmd}))

