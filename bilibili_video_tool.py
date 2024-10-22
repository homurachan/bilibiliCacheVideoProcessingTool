#!/usr/bin/python3
# -*- coding:utf-8 -*-
# For Python 3.5+ , By SpaceSkyNet and Homurachan
# Request to install colorama. Ran 'pip install colorma' if you didn't install this lib.
# Usage: 
# Download danmaku2ass.py from https://github.com/m13253/danmaku2ass
# Replace the danmaku2ass_path = 'D:\danmaku2ass.py' to the actual path.
# Download ffmpeg build and include in the $PATH. One way to do in Windows is to download this ffmpeg windows build: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-full.7z
# and place the ffmpeg.exe and ffprobe.exe into the C:\Windows\system32 folder. You can also manually adjust Environment Variables.
# Run this command: python bilibili_video_tool.py -d 'Your_directory' (Same as the original version)
#
# Changelog:
# No transcoding. Only pack the video and audio streams into a mkv file. If original file is .blv, convert it to .flv.
# Add feature to automatically convert the danmaku.xml to ass file. So you can enjoy all the danmakus with the lastest version of MPC-HC/BE or MPV.
# You can download latest MPC-HC at https://github.com/clsid2/mpc-hc/releases
# The danmaku2ass requires to enter the resolution of video. I use ffprobe to detect the resolution, then pass it to danmaku2ass.
# Adjust codes to suit for old version of mobile caches. The old version entry.json doesn't have "media_type" or "page_data".
import json, os, sys, shutil, platform
import argparse, colorama
from colorama import Fore, Back, Style
import subprocess
danmaku2ass_path = 'D:\danmaku2ass.py'
def get_video_resolution(video_path):
	cmd = [
		'ffprobe', '-v', 'error', '-select_streams', 'v:0',
		'-show_entries', 'stream=width,height', '-of', 'csv=p=0', video_path
	]
	result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
	width=result.stdout.strip().split(',')[0]
	height=result.stdout.strip().split(',')[1]
	return width,height
def replace_illegal_chars(text):
	replace_chars = r'\/:*?"<>|'
	for replace_char in replace_chars:
		text = text.replace(replace_char, ",")
	return text

def get_parts_dirs(workspace_dir):
	parts_dirs = []
	for root, dirs, files in os.walk(workspace_dir, topdown=True):
		for dir in dirs:
			entry_json_path = os.path.join(workspace_dir, dir, 'entry.json')
			if os.path.exists(entry_json_path):
				parts_dirs.append(os.path.join(workspace_dir, dir))
		if len(parts_dirs) == 0:
			print(Fore.RED + "[Error]: No video parts!" + Style.RESET_ALL)
			sys.exit(0)
		else:
			entry_json_path = "entry.json"
			with open(os.path.join(parts_dirs[0], entry_json_path), 'r', encoding='utf-8') as f:
				text = json.loads(f.read())
			export_path = os.path.join(workspace_dir, "..", replace_illegal_chars(text["title"]))
			if not os.path.exists(export_path): os.mkdir(export_path)
			return export_path, parts_dirs

def get_media_type(parts_dir):
	entry_json_path = "entry.json"
	print(parts_dir)
	media_type = 1
	# set default media_type=1. Old version doesn't include mediatype
	with open(os.path.join(parts_dir, entry_json_path), 'r', encoding='utf-8') as f:
		text = json.loads(f.read())
	try:
		media_type = text["media_type"]
	except:
		media_type = 1
	return media_type

def media_type_1(export_path, parts_dir): # merge *.flv (*.blv) | for others
	entry_json_path = "entry.json"
	entry_json_full_path = os.path.join(parts_dir, entry_json_path)
	merge_cmd = 'ffmpeg -f concat -i {} -c copy -bsf:a aac_adtstoasc -movflags +faststart {}'

	with open(entry_json_full_path, 'r', encoding='utf-8') as f:
		text = json.loads(f.read())
	try:
		file_name = replace_illegal_chars(text["page_data"]["part"])
	except:
		file_name = replace_illegal_chars(text["ep"]["index"])
		# set file_name to ep:index. Old version doesn't have page_data:part
	type_tag = text["type_tag"]

	video_parts_dir = os.path.join(parts_dir, type_tag)
	work_dir = os.path.abspath(os.getcwd())
	index_json_path = "index.json"
	video_merged_path = "video.flv"
	video_merged_full_path = os.path.join(video_parts_dir, "video.flv")
	video_merge_info = "mylist.txt"

	os.chdir(video_parts_dir)
	with open(index_json_path, 'r', encoding='utf-8') as f:
		text = json.loads(f.read())
	video_parts = len(text["segment_list"])

	with open(video_merge_info, "w", encoding='utf-8') as f:
		for j in range(0, video_parts):
			f.write("file '{}.{}'\n".format(j, "blv"))

	os.system(merge_cmd.format(video_merge_info, video_merged_path))
	os.chdir(work_dir)

	video_out_path = os.path.join(export_path, "%s.flv" % file_name)
	shutil.move(video_merged_full_path, video_out_path)
	resolution_width, resolution_height = get_video_resolution(video_out_path)
	print("Video resolution",resolution_width,resolution_height)
	danmaku_xml_path = "danmaku.xml"
	danmaku_full_path = os.path.join(parts_dir, danmaku_xml_path)
	danmaku_convert_path = "danmaku.ass"
	danmaku_convert_full_path=os.path.join(parts_dir, danmaku_convert_path)
	danmaku_out_path= os.path.join(export_path, "%s.ass" % file_name)
	run_command = "python "+danmaku2ass_path+" "+danmaku_full_path+" -o "+danmaku_convert_full_path+" -s "+str(resolution_width)+"x"+str(resolution_height)
	os.system(run_command)
	shutil.move(danmaku_convert_full_path, danmaku_out_path)
	print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

def media_type_2(export_path, parts_dir): # mix video.m4s audio.m4s (*.mkv) | for 1080P+
	entry_json_path = "entry.json"
	entry_json_full_path = os.path.join(parts_dir, entry_json_path)
	mix_cmd = 'ffmpeg -i {0} -i {1} -c:v copy -c:a copy -map 0:v:0 -map 1:a:0  {2}'
	mix_cmd_no_audio = 'ffmpeg -i {0} -c:v copy -map 0:v:0 {1}'

	with open(entry_json_full_path, 'r', encoding='utf-8') as f:
		text = json.loads(f.read())
	try:
		file_name = replace_illegal_chars(text["page_data"]["part"])
	except:
		file_name = replace_illegal_chars(text["ep"]["index"])
	type_tag = text["type_tag"]

	video_parts_dir = os.path.join(parts_dir, type_tag)
	video_full_path = os.path.join(video_parts_dir, "video.m4s")
	audio_full_path = os.path.join(video_parts_dir, "audio.m4s")
	video_mixed_full_path = os.path.join(video_parts_dir, "video.mkv")

	if os.path.exists(audio_full_path): os.system(mix_cmd.format(video_full_path, audio_full_path, video_mixed_full_path))
	else: os.system(mix_cmd_no_audio.format(video_full_path, video_mixed_full_path))
	video_out_path = os.path.join(export_path, "%s.mkv" % file_name)
	shutil.move(video_mixed_full_path, video_out_path)
	resolution_width, resolution_height = get_video_resolution(video_out_path)
	print("Video resolution",resolution_width,resolution_height)
	danmaku_xml_path = "danmaku.xml"
	danmaku_full_path = os.path.join(parts_dir, danmaku_xml_path)
	danmaku_convert_path = "danmaku.ass"
	danmaku_convert_full_path=os.path.join(parts_dir, danmaku_convert_path)
	danmaku_out_path= os.path.join(export_path, "%s.ass" % file_name)
	run_command = "python "+danmaku2ass_path+" "+danmaku_full_path+" -o "+danmaku_convert_full_path+" -s "+str(resolution_width)+"x"+str(resolution_height)
	os.system(run_command)
	shutil.move(danmaku_convert_full_path, danmaku_out_path)
	print(Fore.GREEN + "[Process]: {} is finished!".format(file_name) + Style.RESET_ALL)

def check_ffmpeg():
	env_paths = os.environ["PATH"].split(';' if platform.system() == 'Windows' else ":")
	ffmpeg_file = "ffmpeg{}".format(".exe" if platform.system() == 'Windows' else "")
	for env_path in env_paths:
		if os.path.exists(os.path.join(env_path, ffmpeg_file)): return True
	return False

def video_processing(workspace_dir):
	if not check_ffmpeg(): 
		print(Fore.YELLOW + "[Warning]: Can not find ffmpeg in path! \nContinue(y/n)? " + Style.RESET_ALL, end = "")
		op = input()
		if op.lower() in ['y', 'yes']: 
			print(Fore.YELLOW + "[Warning]: Maybe cause some error..." + Style.RESET_ALL)
		else: 
			print(Fore.YELLOW + "[Warning]: Please make sure ffmpeg is in path!" + Style.RESET_ALL)
			sys.exit(0)
	if os.path.exists(workspace_dir):
		export_path, parts_dirs = get_parts_dirs(workspace_dir)
	else:
		print(Fore.RED + "[Error]: No such dir!" + Style.RESET_ALL)
		sys.exit(0)
	for parts_dir in parts_dirs:
		eval("media_type_{}(export_path, parts_dir)".format(get_media_type(parts_dir)))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="bilibili download video mixer / merger by SpaceSkyNet", usage='%(prog)s [options]')
	parser.add_argument("-d", "--dir", type=str, help="the workspace_dir")
	args = parser.parse_args()
	colorama.init()

	if args.dir:
		video_processing(args.dir)
	else:
		parser.print_help()
