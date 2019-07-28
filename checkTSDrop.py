import datetime
import glob
import json
import os
import subprocess
import traceback
from config import *


test_result = """- Multi2DecDos Ver.2.10 - http://2sen.dip.jp/dtv/

Now Processing...

0%                                50%                                100%
|-----+------+------+------+------|------+------+------+------+------|
||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

Input File: g:\pt2_rec\BORUTO-ボルト- NARUTO NEXT GENERATIONS 20180421 0700テレビ東京.ts
Length:      2.99 GB (3,212,092,236 Byte)

[PID: 0x0000]  In:    18449,  Drop: 0,  Scrambling: 0
[PID: 0x0001]  In:      185,  Drop: 0,  Scrambling: 0
[PID: 0x0010]  In:     1845,  Drop: 0,  Scrambling: 0
[PID: 0x0011]  In:      922,  Drop: 0,  Scrambling: 0
[PID: 0x0012]  In:   124641,  Drop: 0,  Scrambling: 0
[PID: 0x0014]  In:      369,  Drop: 0,  Scrambling: 0
[PID: 0x0023]  In:      553,  Drop: 0,  Scrambling: 0
[PID: 0x0024]  In:     1844,  Drop: 0,  Scrambling: 0
[PID: 0x0027]  In:     6226,  Drop: 0,  Scrambling: 0
[PID: 0x0028]  In:       51,  Drop: 0,  Scrambling: 0
[PID: 0x0029]  In:       64,  Drop: 0,  Scrambling: 0
[PID: 0x0100]  In: 12078320,  Drop: 0,  Scrambling: 0
[PID: 0x0110]  In:   327665,  Drop: 0,  Scrambling: 0
[PID: 0x0130]  In:     3394,  Drop: 0,  Scrambling: 0
[PID: 0x0138]  In:     1845,  Drop: 0,  Scrambling: 0
[PID: 0x0140]  In:   193442,  Drop: 0,  Scrambling: 0
[PID: 0x015F]  In:     1846,  Drop: 0,  Scrambling: 0
[PID: 0x0160]  In:  3142199,  Drop: 0,  Scrambling: 0
[PID: 0x0161]  In:   467739,  Drop: 0,  Scrambling: 0
[PID: 0x01F0]  In:    36898,  Drop: 0,  Scrambling: 0
[PID: 0x01FF]  In:    31900,  Drop: 0,  Scrambling: 0
[PID: 0x0338]  In:     1845,  Drop: 0,  Scrambling: 0
[PID: 0x04F0]  In:    36898,  Drop: 0,  Scrambling: 0
[PID: 0x05F0]  In:    36898,  Drop: 0,  Scrambling: 0
[PID: 0x0E01]  In:    18449,  Drop: 0,  Scrambling: 0
[PID: 0x0E02]  In:    18449,  Drop: 0,  Scrambling: 0
[PID: 0x0E11]  In:    69169,  Drop: 0,  Scrambling: 0
[PID: 0x1080]  In:    71117,  Drop: 0,  Scrambling: 0
[PID: 0x1081]  In:   299403,  Drop: 0,  Scrambling: 0
[PID: 0x1083]  In:    71587,  Drop: 0,  Scrambling: 0
[PID: 0x1087]  In:      508,  Drop: 0,  Scrambling: 0
[PID: 0x108B]  In:     3678,  Drop: 0,  Scrambling: 0
[PID: 0x10FF]  In:     7975,  Drop: 0,  Scrambling: 0
[PID: 0x1FC8]  In:     9224,  Drop: 0,  Scrambling: 0

Sync Error       :            0
Format Error     :            0
Transport Error  :            0 Packet
Total Drop Error :            0 Packet
Total Scrambling :            0 Packet

Total Input      :   17,085,597 Packet
Packet Stride    :          188 Byte
"""


def read_result(result):
    lines = result.splitlines()
    dat = {}
    pids = []
    for line in lines:
        if line.find("Sync Error") == 0:
            elms = line.split(":")
            dat["syncError"] = int(elms[1].replace(",", "").replace(" ", ""))
        elif line.find("Format Error") == 0:
            elms = line.split(":")
            dat["formatError"] = int(elms[1].replace(",", "").replace(" ", ""))
        elif line.find("Transport Error") == 0:
            elms = line.split(":")
            dat["transportError"] = int(elms[1].replace("Packet", "").replace(",", "").replace(" ", ""))
        elif line.find("Total Drop Error") == 0:
            elms = line.split(":")
            dat["totalDropError"] = int(elms[1].replace("Packet", "").replace(",", "").replace(" ", ""))
        elif line.find("Total Scrambling") == 0:
            elms = line.split(":")
            dat["totalScrambling"] = int(elms[1].replace("Packet", "").replace(",", "").replace(" ", ""))
        elif line.find("[PID:") == 0:
            index = line.find("]")
            pid = line[1:index].split(":")
            pid_info = {}
            pid_info[pid[0]] = pid[1].replace(" ", "")
            elms = line[index + 1:].split(",")
            for elm in elms:
                arr = elm.split(":")
                pid_info[arr[0].replace(" ", "")] = int(arr[1].replace(",", "").replace(" ", ""))
            pids.append(pid_info)
    dat["pids"] = pids
    return dat


def check_ts_error(path):
    out = subprocess.run([MULTI2DEC_EXE_PATH, "/C", "/N", path], stdout=subprocess.PIPE)
    string = ""
    try:
        string = out.stdout.decode("Shift_JISx0213")
    except:
        traceback.print_exc()
        print(path)
    dat = {}
    if len(string) > 0:
        dat = read_result(string)
        if "totalDropError" in dat and dat["totalDropError"] > 0:
            drop = 0
            size = 0
            for pid in dat["pids"]:
                if pid["In"] > size:
                    size = pid["In"]
                    drop = pid["Drop"]
            if drop > 0:
                with open(path + "drop", "w") as f:
                    f.write(json.dumps(dat))
            dat["maxDrop"] = drop
        else:
            dat["maxDrop"] = 0
    #print(dat)
    return dat


def load_cache_data(file_path: str) -> {}:
    data = {}
    if (os.path.exists(file_path)):
        with open(file_path, "r") as f:
            string = f.read()
            if len(string):
                dat = json.loads(string)
                if dat["data"]:
                    data = dat["data"]
    
    return data


def check_files_in_directory(dir_path: str, cache_data: {}) -> {}:
    files = glob.glob(os.path.join(dir_path, "*"))
    for path in files:
        if path.endswith(".ts") and os.path.basename(path).startswith("タイトル未定") is False:
            if path not in cache_data:
                f = None
                try:
                    f = open(path, "a")
                except:
                    traceback.print_exc()
                if f != None:
                    f.close()
                    print(path)
                    dat = check_ts_error(path)
                    if len(dat):
                        cache_data[path] = dat

    return cache_data


def save_cache_data(file_path: str, cache_data: {}):
    with open(file_path, "w") as f:
        f.seek(0)
        data = {}
        data["date"] = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        data["data"] = cache_data
        f.write(json.dumps(data))


if __name__ == "__main__":
    cache = load_cache_data(DROP_CHECK_OUTPUT_PATH)
    to_delete =[]
    for path in cache:
        if os.path.exists(path) is False:
            to_delete.append(path)
        else:
            pass#print(path)
    for path in to_delete:
        cache.pop(path)

    results = check_files_in_directory(VIDEO_DIR_PATH, cache)

    #dat = read_result(test_result)
    #print(dat)

    #print(cache)
    save_cache_data(DROP_CHECK_OUTPUT_PATH, results)
