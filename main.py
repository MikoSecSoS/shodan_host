#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import re
import time
import random
import argparse

import IPy
import requests

from multiprocessing import Pool
from concurrent.futures import ThreadPoolExecutor

class Shodan:

	def __init__(self, ip):
		self.url = "https://www.shodan.io/host/" + ip
		self.header = 	header = {
				"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
				"accept-language": "zh-CN,zh;q=0.9",
				"alexatoolbar-alx_ns_ph": "AlexaToolbar/alx-4.0.3",
				"cache-control": "max-age=0",
				"cookie": "__cfduid=d45225740608cb4a5b77bb45aa78f1c571560847013; _ga=GA1.2.122797226.1560847121; _gid=GA1.2.1849769871.1562476337; _gat=1; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1",
				"upgrade-insecure-requests": "1",
				"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
			}

	def infoFormat(self, text):
		regex = "<td>(.*?)</td>\n<th>(.*?)</th>"
		result = re.findall(regex, text)
		return result

	def portFormat(self, text):
		regex = "<li><a href=\"#\d+\">(\d+)</a>\n</li>"
		result = re.findall(regex, text)
		return result

	def __service_detailsFormat(self, text):
		regex = ('<div class="service-details">\n'+
						'<div class="port">(\d+)</div>\n'+
						'<div class="protocol">(.*?)</div>\n'+
						'<div class="state">(.*?)</div>')
		result = re.findall(regex, text, re.S)
		return result

	def __service_mainFormat(self, text):
		regex = '<div class="service-main">(.*?)</div>\n</li>'
		result_temp = re.findall(regex, text, re.S)
		result = []
		for r in result_temp:
			r = r.replace("<h3>", "").replace("</h3>", "").replace("<small>", " [").replace("</small>", "]").replace("<pre>", "").replace("</pre>", "").replace("<div class=\"clear\">", "").replace("<div>", "").replace("</div>", "").replace("<h4>", "").replace("</h4>", "\n").replace("<h3>", "").replace("</h3>", "\n")
			result.append(r)
		return result

	def serviceFormat(self, text):
		service_details = self.__service_detailsFormat(text)
		service_main = self.__service_mainFormat(text)
		return (service_details, service_main)

	def spider(self):
		# proxy = requests.get("http://127.0.0.1:5000/get").text
		# proxies = {
		# 	"http": "http://" + proxy
		# }
		# print(proxy)
		# req = requests.get(self.url, headers=self.header, proxies=proxies)
		req = requests.get(self.url, headers=self.header)
		req.encoding = "utf-8"
		if req.status_code == 200:
			return req.status_code
		elif req.status_code == 503:
			print("[503]", self.url)
			self.spider()
		else:
			return req.status_code

def read_lines(path):
	if not os.path.exists(path):
		print("[Error] path %s not found."%(path))
	else:
		file = open(path, "r")
		readlines = file.readlines()
		file.close()
		return readlines

def ipFormat(ip):
	ips = [ip.strNormal() for ip in IPy.IP(ip)]
	return ips

def download(filename, data):
	filename = filename.replace("/", "_")+".txt"
	with open(filename, "a+") as f:
		f.write(str(data)+"\n")

def main(ip):
	shodan = Shodan(ip)
	time.sleep(random.randint(5,8))
	req = shodan.spider()
	if req != 200:
		print("[status_code]  {}.  ip: {}".format(req, ip))
		return
	info   = shodan.infoFormat(req.text)
	ports = shodan.portFormat(req.text)
	service_details, service_main = shodan.serviceFormat(req.text)
	print(dict(info))
	download(ip, info)
	print(ports)
	download(ip, ports)
	for n in range(len(service_details)):
		print(list(service_details[n]))
		download(ip, list(service_details[n]))
		print()
		print(service_main[n])
		download(ip, service_main[n])
		print("="*50)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("-f", "--file", help="Give me a file path")
	parser.add_argument("-i", "--ip", help="Give me ip")
	args = parser.parse_args()
	if args.file:
		path = glob.glob(args.file)
		for p in path:
			for ip in read_lines(p): main(ip)
	elif args.ip:
		ips = ipFormat(args.ip)
		# [main(ip) for ip in ips]
		with ThreadPoolExecutor(10) as p:
			[p.submit(main, ip) for ip in ips]