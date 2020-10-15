try: 
	from BeautifulSoup import BeautifulSoup
except ImportError:
	from bs4 import BeautifulSoup
import os
#from lxml import etree
#from io import StringIO, BytesIO
from parse_hh_data import download, parse
import json
import re

RESUME_LIST_HTML_FILENAME = "ResumeList.html"
HTML_DIR = "html"
RESUME_IDS_FILENAME = "resume-ids.txt"
JSON_DIR = "json"

# from html.parser import HTMLParser

# class MyHTMLParser(HTMLParser):
	# links = []
	# def handle_starttag(self, tag, attrs):
		# if tag == 'a':
			# attributes = dict(attrs)
			# if "href" in attributes:
				# self.links.append(attributes["href"])


	# def handle_endtag(self, tag):
		# print("Encountered an end tag :", tag)

	# def handle_data(self, data):
		# print("Encountered some data  :", data)

# parser = MyHTMLParser()

def prepare_dirs():
	if not os.path.isdir(HTML_DIR):
		os.makedirs(HTML_DIR)
	if not os.path.isdir(JSON_DIR):
		os.makedirs(JSON_DIR)

def get_resume_list_html_path():
	return os.path.join(HTML_DIR, RESUME_LIST_HTML_FILENAME)

def download_resume_list(resume_list_url): 
	import urllib.request as urllib2
	try:
		c = urllib2.urlopen(resume_list_url)
		html = c.read()
		with open(get_resume_list_html_path(), "w", encoding="utf-8") as f:
			f.write(html)
		return html
	except:
		print("Could not open %s" % resume_list_url)

def extract_resume_ids(parsed_html):
	links = parsed_html.body.findAll('a', attrs={'class':'resume-search-item__name'})
	with open(RESUME_IDS_FILENAME, "w") as f:
		for link in links:
			print(link.get("href").split("?")[0].split("/")[-1], file=f)
	
def extract_phone(parsed_html):
	parsed_html = BeautifulSoup(html, features="lxml")
	links = parsed_html.body.findAll('div', attrs={'class':'resume-search-item__name'})
	with open(RESUME_IDS_FILENAME, "w") as f:
		for link in links:
			print(link.get("href").split("?")[0].split("/")[-1], file=f)

def extract_data(parsed_html, elems):
	with open(RESUME_IDS_FILENAME, "w", encoding="utf-8") as f:
		for elem in elems:
			data = parsed_html.body.findAll(elem[0], elem[1])
			for p in data:
				print(p.text, file=f)

 # -*- coding: utf-8 -*-

"""
Extract text in RTF Files. Refactored to use with Python 3.x
Source:
    http://stackoverflow.com/a/188877
Code created by Markus Jarderot: http://mizardx.blogspot.com
"""

import re


def striprtf(text):
	pattern = re.compile(r"\\([a-z]{1,32})(-?\d{1,10})?[ ]?|\\'([0-9a-f]{2})|\\([^a-z])|([{}])|[\r\n]+|(.)", re.I)
	# control words which specify a "destionation".
	destinations = frozenset((
		'aftncn','aftnsep','aftnsepc','annotation','atnauthor','atndate','atnicn','atnid',
		'atnparent','atnref','atntime','atrfend','atrfstart','author','background',
		'bkmkend','bkmkstart','blipuid','buptim','category','colorschememapping',
		'colortbl','comment','company','creatim','datafield','datastore','defchp','defpap',
		'do','doccomm','docvar','dptxbxtext','ebcend','ebcstart','factoidname','falt',
		'fchars','ffdeftext','ffentrymcr','ffexitmcr','ffformat','ffhelptext','ffl',
		'ffname','ffstattext','field','file','filetbl','fldinst','fldrslt','fldtype',
		'fname','fontemb','fontfile','fonttbl','footer','footerf','footerl','footerr',
		'footnote','formfield','ftncn','ftnsep','ftnsepc','g','generator','gridtbl',
		'header','headerf','headerl','headerr','hl','hlfr','hlinkbase','hlloc','hlsrc',
		'hsv','htmltag','info','keycode','keywords','latentstyles','lchars','levelnumbers',
		'leveltext','lfolevel','linkval','list','listlevel','listname','listoverride',
		'listoverridetable','listpicture','liststylename','listtable','listtext',
		'lsdlockedexcept','macc','maccPr','mailmerge','maln','malnScr','manager','margPr',
		'mbar','mbarPr','mbaseJc','mbegChr','mborderBox','mborderBoxPr','mbox','mboxPr',
		'mchr','mcount','mctrlPr','md','mdeg','mdegHide','mden','mdiff','mdPr','me',
		'mendChr','meqArr','meqArrPr','mf','mfName','mfPr','mfunc','mfuncPr','mgroupChr',
		'mgroupChrPr','mgrow','mhideBot','mhideLeft','mhideRight','mhideTop','mhtmltag',
		'mlim','mlimloc','mlimlow','mlimlowPr','mlimupp','mlimuppPr','mm','mmaddfieldname',
		'mmath','mmathPict','mmathPr','mmaxdist','mmc','mmcJc','mmconnectstr',
		'mmconnectstrdata','mmcPr','mmcs','mmdatasource','mmheadersource','mmmailsubject',
		'mmodso','mmodsofilter','mmodsofldmpdata','mmodsomappedname','mmodsoname',
		'mmodsorecipdata','mmodsosort','mmodsosrc','mmodsotable','mmodsoudl',
		'mmodsoudldata','mmodsouniquetag','mmPr','mmquery','mmr','mnary','mnaryPr',
		'mnoBreak','mnum','mobjDist','moMath','moMathPara','moMathParaPr','mopEmu',
		'mphant','mphantPr','mplcHide','mpos','mr','mrad','mradPr','mrPr','msepChr',
		'mshow','mshp','msPre','msPrePr','msSub','msSubPr','msSubSup','msSubSupPr','msSup',
		'msSupPr','mstrikeBLTR','mstrikeH','mstrikeTLBR','mstrikeV','msub','msubHide',
		'msup','msupHide','mtransp','mtype','mvertJc','mvfmf','mvfml','mvtof','mvtol',
		'mzeroAsc','mzeroDesc','mzeroWid','nesttableprops','nextfile','nonesttables',
		'objalias','objclass','objdata','object','objname','objsect','objtime','oldcprops',
		'oldpprops','oldsprops','oldtprops','oleclsid','operator','panose','password',
		'passwordhash','pgp','pgptbl','picprop','pict','pn','pnseclvl','pntext','pntxta',
		'pntxtb','printim','private','propname','protend','protstart','protusertbl','pxe',
		'result','revtbl','revtim','rsidtbl','rxe','shp','shpgrp','shpinst',
		'shppict','shprslt','shptxt','sn','sp','staticval','stylesheet','subject','sv',
		'svb','tc','template','themedata','title','txe','ud','upr','userprops',
		'wgrffmtfilter','windowcaption','writereservation','writereservhash','xe','xform',
		'xmlattrname','xmlattrvalue','xmlclose','xmlname','xmlnstbl',
		'xmlopen',
	))
	# Translation of some special characters.
	specialchars = {
		'par': '\n',
		'sect': '\n\n',
		'page': '\n\n',
		'line': '\n',
		'tab': '\t',
		'emdash': '\u2014',
		'endash': '\u2013',
		'emspace': '\u2003',
		'enspace': '\u2002',
		'qmspace': '\u2005',
		'bullet': '\u2022',
		'lquote': '\u2018',
		'rquote': '\u2019',
		'ldblquote': '\201C',
		'rdblquote': '\u201D',
	}
	stack = []
	ignorable = False # Whether this group (and all inside it) are "ignorable".
	ucskip = 1 # Number of ASCII characters to skip after a unicode character.
	curskip = 0 # Number of ASCII characters left to skip
	out = [] # Output buffer.
	for match in pattern.finditer(text):
		word,arg,hex,char,brace,tchar = match.groups()
		if brace:
			curskip = 0
			if brace == '{':
				# Push state
				stack.append((ucskip,ignorable))
			elif brace == '}':
				# Pop state
				ucskip,ignorable = stack.pop()
		elif char: # \x (not a letter)
			curskip = 0
			if char == '~':
				if not ignorable:
					out.append('\xA0')
			elif char in '{}\\':
				if not ignorable:
					out.append(char)
			elif char == '*':
				ignorable = True
		elif word: # \foo
			curskip = 0
			if word in destinations:
				ignorable = True
			elif ignorable:
				pass
			elif word in specialchars:
				out.append(specialchars[word])
			elif word == 'uc':
				ucskip = int(arg)
			elif word == 'u':
				c = int(arg)
				if c < 0: c += 0x10000
				if c > 127: out.append(chr(c)) #NOQA
				else: out.append(chr(c))
				curskip = ucskip
		elif hex: # \'xx
			if curskip > 0:
				curskip -= 1
			elif not ignorable:
				c = int(hex,16)
				if c > 127: out.append(chr(c)) #NOQA
				else: out.append(chr(c))
		elif tchar:
			if curskip > 0:
				curskip -= 1
			elif not ignorable:
				out.append(tchar)
	return ''.join(out)

def process_resume_text(text):
	pass

if __name__ == "__main__":
	prepare_dirs()
	
	if not os.path.isfile(os.path.join(HTML_DIR, RESUME_LIST_HTML_FILENAME)):
		html = download_resume_list("https://pavlodar.hh.kz/search/resume?text=%D1%8E%D1%80%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D1%8D%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%90%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%94%D0%B8%D0%B7%D0%B0%D0%B9%D0%BD%D0%B5%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%94%D0%B8%D1%80%D0%B5%D0%BA%D1%82%D0%BE%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%96%D1%83%D1%80%D0%BD%D0%B0%D0%BB%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9C%D0%B0%D1%80%D0%BA%D0%B5%D1%82%D0%BE%D0%BB%D0%BE%D0%B3&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%91%D1%83%D1%85%D0%B3%D0%B0%D0%BB%D1%82%D0%B5%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=HR&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%A4%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%91%D0%B0%D0%BD%D0%BA&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%93%D0%B5%D0%BE%D0%B4%D0%B5%D0%B7%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9F%D0%BE%D0%B2%D0%B0%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&area=160&relocation=living_or_relocation&salary_from=&salary_to=120000&currency_code=KZT&education=none&age_from=18&age_to=45&gender=male&employment=full&schedule=fullDay&order_by=publication_time&search_period=30&items_on_page=100&no_magic=false")
	else:
		with open(get_resume_list_html_path(), "r", encoding="utf-8") as f:
			html = f.read()
	
	
	if not os.path.isfile(RESUME_IDS_FILENAME):
		extract_resume_ids(html, elems)
	
	# extract resume IDs
	#with open(RESUME_IDS_FILENAME, "r") as f:
		#resume_ids = [x.replace("\n", "") for x in f.readlines()]
	
	# extract name, phone, etc.
	parsed_html = BeautifulSoup(html, features="lxml")
	elems = [
		("div", {"class": "resume-search-item__fullname"}), # full name
		("span", {"data-qa": "resume-serp__resume-age"}), # age
		("div", {"data-qa": "resume-serp__resume-excpirience-sum"}), # experience
		("div", {"data-hh-last-experience-id": re.compile(r".*")}),
		("div", {"resume-search-item__company-name": re.compile(r".*")})
	]
	
	elems = [
		("div", {"data-qa": "resume-serp__resume"})
	]
	
	#extract_data(parsed_html, elems)
	
	for file in os.listdir("resume")[:5]:
		if file.split(".")[1] == "doc":
			with open("resume/" + file, "r") as f:
				print(file, striprtf(f.read()))
	
	#for ri in resume_ids[:1]:
		#resume = download.resume(ri)
		#with open(os.path.join(JSON_DIR, ri + ".json"), "w") as f:
			#resume = parse.resume(resume)
			#f.write(json.dumps(resume, ensure_ascii=False))
		
