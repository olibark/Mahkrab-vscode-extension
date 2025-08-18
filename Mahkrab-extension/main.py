#!/usr/bin/env python3
import argparse, json, os, sys, platform, shlex

# ---------- args ----------
def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--file', required=True)  # active C file (absolute from VS Code)
    p.add_argument('--cwd',  required=True)  # workspace root
    return p.parse_args()

# ---------- headers -> linker flags ----------
def take_linker_flags(file_location: str) -> str:
    flags = []
    with open(file_location, 'r', encoding='utf-8', errors='ignore') as src:
        for raw in src:
            line = raw.strip()
            if not line.startswith('#include'):
                continue
            header = (line.replace('#include', '')
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
    flags.append('-lSDL2_gfx')

    return ' ' + ' '.join(flags) if flags else ''

# ---------- build command ----------
def make_command(active_file: str, cwd: str, flags: str):
    # compiler choice: clang on macOS (cc), gcc elsewhere; allow $CC override
    cc = os.environ.get('CC') or ('cc' if platform.system().lower().startswith('darwin') else 'gcc')

    name      = os.path.splitext(os.path.basename(active_file))[0]
    build_dir = os.path.join(cwd, 'build')
    exe_path  = os.path.join(build_dir, name)
    if platform.system().lower().startswith('win'):
        exe_path += '.exe'

    # shell-safe quoting
    q_cwd       = shlex.quote(cwd)
    q_build_dir = shlex.quote(build_dir)
    q_src       = shlex.quote(active_file)
    q_exe       = shlex.quote(exe_path)

    compile_cmd = f'{cc} -O0 -g {q_src} -o {q_exe}{flags}'
    run_cmd     = q_exe if platform.system().lower().startswith('win') \
                 else f'./{shlex.quote(os.path.relpath(exe_path, cwd))}'
    full_cmd    = f'cd {q_cwd} && mkdir -p {q_build_dir} && {compile_cmd} && {run_cmd}'
    return compile_cmd, run_cmd, full_cmd

# ---------- main ----------
if __name__ == '__main__':
    args = parse_args()

    # resolve & validate paths
    active_file = os.path.abspath(os.path.expanduser(args.file))
    cwd         = os.path.abspath(os.path.expanduser(args.cwd))

    if not os.path.exists(active_file):
        print(f'ERROR: file not found: {active_file}', file=sys.stderr)
        sys.exit(2)
    if not os.path.isdir(cwd):
        print(f'ERROR: cwd not a directory: {cwd}', file=sys.stderr)
        sys.exit(2)

    flags = take_linker_flags(active_file)
    compile_cmd, run_cmd, full_cmd = make_command(active_file, cwd, flags)

    # <<< THIS is what your extension reads >>>
    print(json.dumps({
        "compile": compile_cmd,
        "run": run_cmd,
        "full": full_cmd
        }
    )  
)