import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

from bs4 import BeautifulSoup
import queue
import threading
import argparse

class discoveryWebCrawlerClass():

	def __init__(self,domain,level):
		self.domain = domain
		self.q = queue.Queue()
		self.urls = []
		self.levelsToCrawl = level

	def crawlURL(self,crawlUrl,currentLevel):
		s = requests.Session()
		r = s.get(crawlUrl,verify=False,timeout=10)
		soup = BeautifulSoup(r.content,'html.parser') 
		links = soup.find_all('a')
		for url in links:
			try:
				url = url.get('href')
				# some href values dont have a full url. They look somthing like : /login.php
				if url[0] == '/':
					url = self.domain + url
				# check to see if link matches crawl domain 
				if url.split("/")[2] == self.domain.split('/')[2] and url not in self.urls:
					self.urls.append(url)
					#insert into queue update crawl level
					if currentLevel+1 < self.levelsToCrawl:
						self.q.put({'url':url,'level':currentLevel +1})
			except Exception as e:
				pass

	def worker(self):
		while 1:
			crawlUrlDict = self.q.get()
			self.crawlURL(crawlUrlDict['url'],crawlUrlDict['level'])
			self.q.task_done()

	def start(self):
		self.q.put({'url':self.domain,'level':0})
		for i in range(0,100):
			t = threading.Thread(target=self.worker)
			t.daemon = True
			t.start()
		self.q.join()



parser = argparse.ArgumentParser()
parser.add_argument("-d","--domain", help="Domain Name; EX: https://test.com")
parser.add_argument("-l","--level", help="Levels deep to crawl. EX: 2")
args = parser.parse_args()

if args.domain and args.level:
	webcrawler = discoveryWebCrawlerClass(args.domain,int(args.level))
	webcrawler.start()
	for i in range(0,len(webcrawler.urls)):
		print("{0}\t{1}".format(i,webcrawler.urls[i]))
