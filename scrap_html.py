"""
Usage: 
>>> python scrap_html.py
"""

import urllib.request
from bs4 import BeautifulSoup
import json

TITLES = {
	'genesis':50, # number of chapters
	'exodus':40,
	'leviticus':27,
	'numbers':36,
	'deuteronomy':34
}

from pathlib import Path
parseurl = lambda url: urllib.request.urlopen(url).read()

class ScrapMTT:
	"""
	Scrap Mechanical Translation from
	http://www.mechanical-translation.org/mtt/G1.html
	to JSON File
	"""
	def __init__(self):
		self.url = 'http://www.mechanical-translation.org/mtt'

	def get_htmlfile_path(self,title,chapter):
		# html/G1.html
		f = 'html/{t}{c}.html'.format(t= title[0].capitalize(), c= chapter) 
		return Path(f)

	def save_html(self,title,chapter):
		"""
		Save Website as html file
		"""	
		p = self.get_htmlfile_path(title,chapter)
		if p.exists(): 
			print('file exists',p)
			return ''
		html_doc = parseurl('{url}/{t}{c}.html'.format(url = self.url, t=title[0].capitalize(),c=chapter))

		with p.open('wb') as fp:
			fp.write(html_doc)
			fp.close()

	def html_to_json(self, html_doc):
		"""
		Convert an HTML file to JSON
		"""
		soup = BeautifulSoup(html_doc, 'html.parser')
		lines = []
		for i,table in enumerate(soup.find_all('table')):
			for td in table.find_all('td'):
				for line in td('p'):					
					cur_word = []
					cur_line = []
					for word in line('a'):						
						cur_word.append(word.get_text())						
						if '(' in word.next_sibling:
							cur_line.append(' '.join(cur_word))
							cur_word=[]
					if cur_line: 
						lines.append(cur_line)
		return lines

	def parse_chapter(self, title, chapter):
		"""
		Parse html to JSON
		"""
		p = self.get_htmlfile_path(title,chapter)
		if not p.exists(): 
			print('downloading title:%s, chapter:%s' %(title,chapter))
			self.save_html(title,chapter)

		with p.open() as fp:
			html_doc = fp.read()

		return self.html_to_json(html_doc)


	def save_json(self,title):
		data = { 
		    "versionTitle": "Paleo Hebrew Word by Word, http://www.mechanical-translation.org/mtt/G1.html",
		    "language": "eg", 
		    "title": title,
		    'text':[]
		}
		for chapter in range(1,TITLES[title]+1):
			# eg: range(1,51) for genesis
			# if chapter != 1: continue
			data['text'].append( self.parse_chapter(title,chapter))

		with open('%s.json'%title, 'w') as outfile:
		    json.dump(data, outfile,indent = 4)

		

	def scrap(self):
		for key,value in TITLES.items():
			# if key != 'genesis': continue
			self.save_json(key)

if __name__=='__main__':
	scraper = ScrapMTT()
	scraper.scrap()