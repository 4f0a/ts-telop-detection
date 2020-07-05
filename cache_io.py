import datetime
import json
import os
import time


def load_cache_data(file_path: str) -> {}:
	data = {}
	if (os.path.exists(file_path)):
		data = None
		with open(file_path, "r") as f:
			string = f.read()
			if len(string):
				dat = json.loads(string)
				if dat["data"]:
					data = dat["data"]
				else:
					data = {}
	return data


def rename_file(src_path: str, dest_path: str, retry_count: int) -> bool:
	if os.path.exists(dest_path):
		try:
			os.remove(dest_path)
			os.rename(src_path, dest_path)
			return True
		except OSError as e:
			print(e)
			if retry_count > 0:
				time.sleep(1)
				return rename_file(src_path, dest_path, retry_count - 1)
			return False
	else:
		os.rename(src_path, dest_path)
		return True


def save_cache_data(file_path: str, cache_data: {}, retry_count: int = 5):
	tmp_path = file_path + datetime.datetime.today().strftime("%Y-%m-%d-%H-%M-%S-%f")

	with open(tmp_path, "w") as f:
		data = {}
		data["date"] = datetime.datetime.today().strftime("%Y/%m/%d %H:%M:%S")
		data["data"] = cache_data
		f.write(json.dumps(data))

	return rename_file(tmp_path, file_path, retry_count)

