import datetime
import glob
import hashlib
import json
import os
import shutil
import subprocess
import traceback
import cache_io
from config import *


def save_frame_as_image(video_path, fps, output_dir):
    result = subprocess.run(["ffmpeg", "-i", video_path, "-ss", "0", "-vframes", "1", "-f", "image2", os.path.join(output_dir, "0000.jpg")])
    if result.returncode == 0:
        result = subprocess.run(["ffmpeg", "-i", video_path, "-filter:v", "fps=fps=" + str(fps) + ":round=down", os.path.join(output_dir, "%04d.jpg")])
    return result.returncode


def output_dir_name_for_file(file_path):
    #return os.path.join("data", "frames", os.path.basename(file_path)).replace("#", "＃")
    file_name = os.path.basename(file_path)
    return hashlib.sha256(file_name.encode()).hexdigest()


mx_acception = [
    "ルパン三世",
    "おこしやす、ちとせちゃん",
    "エガオノダイカ",
    "不機嫌なモノノケ庵",
    "モブサイコ",
    "ぱすてるメモリーズ",
    "サークレット・プリンセス",
    "臨死",
    "雨色ココア",
    "ケムリクサ",
    "明治東亰恋伽",
    "バーチャルさんはみている",
    "この世の果てで恋を唄う少女",
    "群青のマグメル",
    "洗い屋さん",
    "八十亀ちゃんかんさつにっき",
    "ふたばにめ",
    ]

def should_process_for_file(file_path):
    if os.path.getsize(file_path) == 0:
        return False
    if file_path.endswith(".ts") is False and file_path.endswith(".m2ts") is False:
        return False
    if file_path.find("タイトル未定") >= 0:
        return False
    if file_path.find("ＮＨＫＢＳプレミアム") >= 0:
        return False
    if file_path.find("ＮＨＫＢＳ１") >= 0:
        return False
    """if file_path.find("ＴＯＫＹＯ　ＭＸ") >= 0:
        for name in mx_acception:
            if file_path.find(name) >= 0:
                return True
        return False"""
    if file_path.find("のど自慢") >= 0:
        return False
    return True


def sample_frames_of_files_in_directory(dir_path: str, output_dir_path: str):
    files = glob.glob(os.path.join(dir_path, "*"))
    for path in files:
        print(path)
        if os.path.isfile(path) and should_process_for_file(path):
            out_path = os.path.join(output_dir_path, output_dir_name_for_file(path))
            print("dir path: " + out_path)
            tmp_path = out_path + "_tmp"
            if os.path.exists(out_path) is False and os.path.exists(tmp_path) is False:
                # neither created or under creation
                f = None
                try:
                    f = open(path, "a")
                except:
                    traceback.print_exc()
                if f != None:
                    f.close()
                    print(path)
                    os.makedirs(tmp_path)
                    save_frame_as_image(path, 0.12, tmp_path)
                    shutil.move(tmp_path, out_path)
            else:
                print("should not process.")
        else:
            print("not a target.")


if __name__ == "__main__":
    cache = cache_io.load_cache_data(TELOP_CHECK_OUTPUT_PATH)
    if cache == None:
        exit()

    to_delete =[]
    for path in cache:
        if os.path.exists(path) is False or os.path.isdir(path):
            to_delete.append(path)
        else:
            pass#print(path)

    # delete cache for those does not exist
    for path in to_delete:
        dir_path = os.path.join(SAMPLED_FRAMES_CACHE_DIR_PATH, output_dir_name_for_file(path))
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        cache.pop(path)

    cache_io.save_cache_data(TELOP_CHECK_OUTPUT_PATH, cache)

    sample_frames_of_files_in_directory(VIDEO_DIR_PATH, SAMPLED_FRAMES_CACHE_DIR_PATH)
