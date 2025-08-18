"""import json
import os

def take_linker_flags(file_location):
    flags = ''
    with open(file_location, 'r') as src:
        for line in src:
            if not line.strip().startswith('#include'):
                continue
            header = (line
                      .replace('#include', '')
                      .replace('<', '')
                      .replace('>', '')
                      .strip())
            if header == 'SDL2/SDL.h':
                flags += ' -lSDL2'
            elif header == 'SDL2/SDL_image.h':
                flags += ' -lSDL2_image'
            elif header == 'SDL2/SDL_ttf.h':
                flags += ' -lSDL2_ttf'
            elif header == 'curl/curl.h':
                flags += ' -lcurl'
            elif header == 'jansson.h':
                flags += ' -ljansson'
            elif header == 'openssl/sha.h':
                flags += ' -lssl -lcrypto'
            elif header == 'gtk/gtk.h':
                flags += ' `pkg-config --cflags --libs gtk+-3.0`'
            elif header == 'zlib.h':
                flags += ' -lz'
            elif header == 'ncurses.h':
                flags += ' -lncurses'
    return flags

def update_settings_json(c_command):
    """"""
    Load settings.json, update the C executorMap entry, and write it back.
    """"""
    settings_path = '/Library/Application Support/Code/User/settings.json'
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    # Update the C compile-and-run command using the naming convention
    settings['code-runner.executorMap']['c'] = c_command
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)

if __name__ == '__main__':
    # Path to the source file; you could also take this from argv
    source_file = input("Enter the path to the C source file: ")
    # Compute linker flags based on dependencies
    linker_flags = take_linker_flags(source_file)
    # Build the compile-and-run command using placeholders
    compile_and_run = (
        f"cd $dir && mkdir -p build && "
        f"gcc $fileName -o build/$fileNameWithoutExt{linker_flags} && "
        f"./build/$fileNameWithoutExt"
    )
    # Update the JSON configuration
    update_settings_json(compile_and_run)
    print("Compile and run command:")
    print(compile_and_run)"""
    
    
import json, os
import argparse as ap

def findFile():
    parser = ap.ArgumentParser()
    parser.add_argument('--file', required = True)
    parser.add_argument('--cwd', required = True)
    args = parser.parse_args()
    
    activeFile = args.file
    workingDir = args.cwd
    
    return activeFile, workingDir

activeFile, workingDir = findFile()
print(f"Active file: {activeFile}")
print(f"Working directory: {workingDir}")

