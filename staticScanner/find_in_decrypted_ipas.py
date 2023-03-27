#!/usr/bin/env python

import sys
import os
import zlib

import scandir
import subprocess
#from queue import queue
import queue
import argparse
import threading
import traceback
import signal
import time
import zipfile
import biplist
import plistlib
import shutil
import json
import zipfile

grep_queue = queue.Queue()
matched_result = {}
all_put = False
killed = False

def create_tmp_dir():
    import tempfile
    return tempfile.mkdtemp()

global_tmp_dirpath = None
def get_tmp_dir():
    global global_tmp_dirpath
    if None is global_tmp_dirpath:
        global_tmp_dirpath = create_tmp_dir()
    return global_tmp_dirpath

def get_infoplist_of_ipa(ipa_filepath):
    zf = None
    pl = None
    try:
        zf = zipfile.ZipFile(ipa_filepath, 'r')
        for filename in zf.namelist():
            filename_parts = filename.split("/")
            if len(filename_parts) == 3 and filename_parts[0] == "Payload" and filename_parts[2] == "Info.plist":
                info_plist_data = zf.read(filename)
                if sys.version_info[0] == 2:
                    pl = biplist.readPlistFromString(info_plist_data)
                else:
                    pl = plistlib.loads(info_plist_data)
                break
    except Exception:
        pass
    finally:
        if zf:
            zf.close()
    return pl

def extract_main_exe_from_ipa(ipa_filepath, dst_filepath):
    if not (os.path.isfile(ipa_filepath) and os.path.getsize(ipa_filepath) != 0):
        return None
    info_pl = get_infoplist_of_ipa(ipa_filepath)
    if None is info_pl:
        return None
    main_exe_name = info_pl.get("CFBundleExecutable")
    if None is main_exe_name:
        return None
    #main_exe_name = main_exe_name.encode("utf8")
    #main_exe_name = main_exe_name.decode()

    zf = None
    exe_filepath = None
    try:
        zf = zipfile.ZipFile(ipa_filepath, 'r')
        with open("/dev/null", "w") as DEVNUL:
            for fileinfo in zf.infolist():
                filename = fileinfo.filename
                filename_parts = filename.split("/")
                if len(filename_parts) == 3 and filename_parts[0] == "Payload":
                    if filename_parts[2] == main_exe_name:
                        tmp_dirpath = create_tmp_dir()
                        try:
                            zf.extract(fileinfo, tmp_dirpath)
                        except zlib.error:
                            traceback.print_exc()
                            subprocess.call(["unzip", "-f", ipa_filepath, filename, "-d", tmp_dirpath], stdout=DEVNUL)
                        exe_filepath = dst_filepath
                        shutil.move(os.path.join(tmp_dirpath, filename), exe_filepath)
                        shutil.rmtree(tmp_dirpath)
                        break
    except Exception:
        traceback.print_exc()
    finally:
        if zf:
            zf.close()
    return exe_filepath

def grep_in_main_exec(exec_path, words):
    matched_words = []
    with open(exec_path, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
        for word in words:
            if word in content:
                matched_words.append(word) 
    return matched_words

def grep_in_ipa_info(filepath, words):
    if not (os.path.isfile(filepath) and os.path.getsize(filepath) != 0):
        return []
    matched_words = []
    try:
        info = get_infoplist_of_ipa(filepath)
        if info:
            for word in words:
                if word in info.keys() or word in info.values():
                    matched_words.append(word)
    except Exception as e:
        traceback.print_exc()
    return matched_words

def grep_in_ipa(filepath, words, for_infoplist):
    if for_infoplist:
        return grep_in_ipa_info(filepath, words)

    if not (os.path.isfile(filepath) and os.path.getsize(filepath) != 0):
        return []
    fn = os.path.basename(filepath)
    tmp_exec_filepath = os.path.join(get_tmp_dir(), fn[:-4])
    matched_words = []
    try:
        extracted_path = extract_main_exe_from_ipa(filepath, tmp_exec_filepath)
        if extracted_path:
            matched_words = grep_in_main_exec(tmp_exec_filepath, words)
        else:
            print ("[!] Failed to extract {}".format(filepath))
    except Exception as e:
        traceback.print_exc()
    if os.path.isfile(tmp_exec_filepath):
        os.remove(tmp_exec_filepath)
    return matched_words


def grep_worker(filepath, words, for_infoplist):
    words = set(words)
    global all_put, grep_queue, matched_result, killed
    fn = os.path.basename(filepath)
    #print "[+] grep {} in {}".format(words, filepath) 
    matched_words = grep_in_ipa(filepath, words, for_infoplist)
    if len(matched_words) > 0:
        print ("[+] Found {} in {}".format(matched_words, fn))
    for word in matched_words:
        matched_result[word].append(fn)

working_threads = []

def main(indir, words, for_infoplist):
    print (get_tmp_dir())
    global working_threads, all_put, grep_queue, matched_result, working_thcnt
    #decrypted_ipas_dirpath = os.path.expanduser(indir)
    decrypted_ipas_dirpath = indir
    for word in words:
        matched_result[word] = []
    
    for root, dirs, files in os.walk(decrypted_ipas_dirpath):
        for fn in files:
            if fn.endswith(".ipa"):
                filepath = os.path.join(root, fn)
                while len(working_threads) > 16:
                    for t in list(working_threads):
                        if not t.is_alive():
                            working_threads.remove(t)
                    #print "Main waiting"
                    time.sleep(2)
                
                t = threading.Thread(target=grep_worker, args=(filepath, words, for_infoplist))
                t.daemon = True
                working_threads.append(t)
                t.start()
    while True:
        all_dead = True
        for t in working_threads:
            if t.is_alive():
                all_dead = False
        if all_dead:
            break
        time.sleep(5)

output_filepath = "find_in_decrypted_ret.txt"
def exit_gracefully(a, b):
    global matched_result
    global output_filepath
    print ("[+] Finish scanning, check the result in {}".format(output_filepath))
    with open(output_filepath, "w") as fp:
        json.dump(matched_result, fp)
    exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)
    parser = argparse.ArgumentParser(description='Find in decrypted ipas\' main bin')
    parser.add_argument("-t", "--target", action="append", dest="targets", help="target to find, can be single API")
    parser.add_argument("-f", "--targetfile", dest="targetfile", help="path to file listing all targeted API")
    parser.add_argument("-i", "--indir", dest="indir", help="which dir the app in")
    parser.add_argument("-o", "--output", dest="output", help="output file path, default is find_in_decrypted_ret.txt")
    parser.add_argument("-p", "--infoplist", dest="for_infoplist", action="store_true", help="search in infoplist")
    args = parser.parse_args()
    if (not args.targets) and (not args.targetfile):
        parser.print_help()
        exit(-1)
    targets = args.targets
    if args.targetfile:
        with open(args.targetfile) as fp:
            targets = fp.read().splitlines()
    targets = list(set(targets))
    if args.output:
        output_filepath = args.output
    try:
        main(args.indir, targets, args.for_infoplist)
    except Exception as e:
        traceback.print_exc()
    except KeyboardInterrupt:
        pass
    killed = True

    exit_gracefully(None, None)

