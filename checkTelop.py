import base64
import datetime
import glob
import hashlib
import json
import MeCab
import math
import os
import re
import shutil
import time
import traceback
import urllib.request
from PIL import Image, ImageMath
import sampleFrames
from config import *


def ask_google(image_path):
    with open(image_path, "br") as fimg:
        binary = fimg.read()
        str_base64 = base64.b64encode(binary).decode("utf-8")

        headers = {"Content-Type": "application/json"}

        data = {
            "requests": [
                {
                    "image": {
                        "content": str_base64
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ],
                    "imageContext": {
                        "languageHints": [
                            "ja"
                        ]
                    }
                }
            ]
        }

        req = urllib.request.Request(GOOGLE_API_URL + GOOGLE_API_KEY, json.dumps(data).encode(), headers)
        try:
            with urllib.request.urlopen(req) as res:
                text = res.read().decode()
                #with open("result_json.txt", "w") as f:
                    #f.write(text)
                return json.loads(text)
        except urllib.error.HTTPError as err:
            print(err.code)
            with open(GOOGLE_API_ERROR_OUTPUT_PATH, "a") as log:
                log.write(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S ") + "HTTPError: " + str(err.code) + "\n" + image_path + "\n")
        except urllib.error.URLError as err:
            print(err.reason)
            with open(GOOGLE_API_ERROR_OUTPUT_PATH, "a") as log:
                log.write(datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S ") + "URLError: " + str(err.reason) + "\n" + image_path + "\n")
    return False


def binarize_image(in_path, out_path):
    im = Image.open(in_path)
    if im:
        h, s , v = im.crop((0, 0, im.width, 256)).convert("HSV").split()
        _v = ImageMath.eval("v * (s < 12)", s=s, v=v).convert("L")
        #Image.merge("HSV", (h, s, _v)).convert("RGB").save(out_path)
        Image.merge("HSV", (h, s, _v)).convert("L").point(lambda x: 0 if x < 207 else 255).save(out_path)
        return True
    return False


def binarize_image_2(in_path, out_path):
    im = Image.open(in_path)
    if im:
        im.crop((0, 0, im.width, 256)).convert("L").point(lambda x: 0 if x < 128 else 255).save(out_path)
        return True
    return False


def concat(files, unit_width, unit_height, row, col, dest_path):
	canvas = Image.new("L", (col * unit_width, row * unit_height))
	for i in range(0, row):
		for j in range(0, col):
			if i * col + j < len(files):
				img = Image.open(files[i * col + j])
				canvas.paste(img, (j * unit_width, i * unit_height))
	canvas.save(dest_path)


def rect_from_vertices(vertices):
    x0 = 0
    y0 = 0
    x1 = 0
    y1 = 0
    if len(vertices) > 2:
        if "x" in vertices[0]:
            x0 = vertices[0]["x"]
            x1 = x0
        if "y" in vertices[0]:
            y0 = vertices[0]["y"]
            y1 = y0
    for i in range(1, len(vertices)):
        if "x" in vertices[i]:
            if vertices[i]["x"] < x0:
                x0 = vertices[i]["x"]
            if vertices[i]["x"] > x1:
                x1 = vertices[i]["x"]
        if "y" in vertices[i]:
            if vertices[i]["y"] < y0:
                y0 = vertices[i]["y"]
            if vertices[i]["y"] > y1:
                y1 = vertices[i]["y"]
    return {"x0": x0, "y0": y0, "x1": x1, "y1": y1}


def feed_google_vision_result(result, unit_width, unit_height, row_count, col_count):
    dat = {}
    if "responses" in result and "textAnnotations" in result["responses"][0]:
        annots = result["responses"][0]["textAnnotations"]
        for i in range(1, len(annots)):
            elm = annots[i]
            #print(elm)
            if "description" in elm:
                text = elm["description"]
                if "boundingPoly" in elm and "vertices" in elm["boundingPoly"]:
                    rect = rect_from_vertices(elm["boundingPoly"]["vertices"])
                    col = math.floor(rect["x0"] / unit_width)
                    row = math.floor(rect["y0"] / unit_height)
                    if rect["x1"] <= (col + 1) * unit_width and rect["y1"] <= (row + 1) * unit_height:
                        frm_key = str(col + row * col_count)
                        txt_for_frame = ""
                        if frm_key in dat:
                            txt_for_frame = dat[frm_key]
                        txt_for_frame += text
                        dat[frm_key] = txt_for_frame
    return dat


telop_words = [
    "ニュース",
    "速報",
    "情報",
    "地震",
    "震度",
    "震源",
    "地域",
    "地方", 
    "津波",
    "心配",
    "気象",
    "大雨",
    "洪水",
    "土砂",
    "台風",
    "暴風",
    "波浪",
    "大気",
    "非常",
    "警報",
    "災害",
    "警戒",
    "注意",
    "避難",
    "発表",
    "断水",
    "停電",
    "浸水",
    "氾濫",
    "死亡",
    "不明",
    "県警",
    "警察",
    "殺人",
    "殺害",
    "事件",
    "容疑",
    "逮捕",
    "人質",
    "大使館",
    "決定",
    "事故",
    "全線",
    "運転",
    "再開",
    "見合わせ",
    "選挙",
    "当選",
    "当確",
    "比例",
    "自民",
    "内閣",
    "政府",
    "衆院",
    "参院",
    "五輪",
    "メダル",
    "野球",
    "結果",
    "招致",
    "ミサイル",
    "発射",
    "防衛",
]

def is_string_telop(string):
    string = string.replace(" ", "").replace("\r", "").replace("\n", "")
    if len(string) < 2:
        return False
    if string == "事故対応満足度":
        return False
    for word in telop_words:
        if string.find(word) >= 0:
            return True
    return False


def string_maybe_telop(mcb, string):
    parsed = mcb.parse(string)      # 形態素解析結果（改行を含む文字列として得られる）
    #print(parsed)
    lines = parsed.split('\n')  # 解析結果を1行（1語）ごとに分けてリストにする
    lines = lines[0:-2]         # 後ろ2行は不要なので削除
    #diclist = []
    for word in lines:
        l = re.split('\t|,',word)  # 各行はタブとカンマで区切られてるので
        #d = {'Surface':l[0], 'POS1':l[1], 'POS2':l[2], 'CAT':l[3], 'BaseForm':l[7]}
        #diclist.append(d)
        if l[2] == "固有名詞" and len(l[0]) >= 2:
            if l[3] == "地域":
                return True
    return False


def detect_telopped_image(mcb, dir_path, binarization_mode):
    googled = True
    found = False
    dat = {}
    images = glob.glob(os.path.join(dir_path, "*.jpg"))
    if len(images) == 0:
        return dat
    #print(images)
    pngs = []
    for img_file in images:
        mono = img_file + ".png"
        if binarization_mode == 0:
            if binarize_image(img_file, mono):
                pngs.append(mono)
        else:
            if binarize_image_2(img_file, mono):
                pngs.append(mono)
    im = Image.open(pngs[0])
    width = im.width
    height = im.height
    row = 30
    col = math.floor(6000 / width)
    cycle = math.ceil(len(images) / (row * col))
    for i in range(0, cycle):
        dest_path = os.path.join(dir_path, str(row) + "-" + str(col) + "-" + str(i) + ".png")
        concat(pngs[i * row * col:(i + 1) * row * col], width, height, row, col, dest_path)
        result = ask_google(dest_path)
        if isinstance(result, dict):
            frames = feed_google_vision_result(result, width, height, row, col)
            for num_str in frames:
                rank = 10
                if is_string_telop(frames[num_str]):
                    rank = 0
                    found = True
                elif string_maybe_telop(mcb, frames[num_str]):
                    rank = 1
                dat[images[int(num_str) + i * row * col]] = {"string": frames[num_str], "rank": rank}
        else:
            googled = False
    if googled is False:
        # should try tesseract
        pass
    if binarization_mode == 0 and found is False:
        dat = detect_telopped_image(mcb, dir_path, 1)
    #print(dat)
    return dat


def should_process_file(file_path: str, cache_path: str):
    cache = {}
    if (os.path.exists(cache_path)):
        with open(cache_path, "r") as f:
            string = f.read()
            if len(string):
                dat = json.loads(string)
                if dat["data"]:
                    cache = dat["data"]
    return file_path not in cache


def add_data_to_cache_file(key, item_data, cache_path: str):
    cache = {}
    if (os.path.exists(cache_path)):
        with open(cache_path, "r") as f:
            string = f.read()
            if len(string):
                dat = json.loads(string)
                if dat["data"]:
                    cache = dat["data"]
    cache[key] = item_data
    with open(cache_path, "w") as f:
        f.seek(0)
        data = {}
        data["date"] = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
        data["data"] = cache
        f.write(json.dumps(data))


def check_telop_of_file_in_directory(dir_path: str, frames_dir_path: str, cache_path:str):
    mcb = MeCab.Tagger()

    files = glob.glob(os.path.join(dir_path, "*"))
    for path in files:
        if os.path.isfile(path):
            print(path)
            frames_path = os.path.join(frames_dir_path, sampleFrames.output_dir_name_for_file(path))
            print(frames_path)
            if os.path.exists(frames_path) and should_process_file(path, cache_path):
                start = time.time()
                dat = detect_telopped_image(mcb, frames_path, 0)
                print(time.time() - start)
                #if len(dat):
                add_data_to_cache_file(path, dat, cache_path)


if __name__ == "__main__":
    check_telop_of_file_in_directory(VIDEO_DIR_PATH, SAMPLED_FRAMES_CACHE_DIR_PATH, TELOP_CHECK_OUTPUT_PATH)

