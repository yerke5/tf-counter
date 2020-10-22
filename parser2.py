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
import unicodedata

RESUME_LIST_HTML_FILENAME = "ResumeList.html"
HTML_DIR = "html"
RESUME_IDS_FILENAME = "resume-ids.txt"
JSON_DIR = "json"

RUS_MONTHS = [
	"январь",
	"февраль",
	"март",
	"апрель",
	"май",
	"июнь",
	"июль",
	"август",
	"сентябрь",
	"октябрь",
	"ноябрь",
	"декабрь"
]

class HHResume:
	SECTION_NAMES = [
		"Желаемая должность и зарплата",
		"Опыт работы",
		"Ключевые навыки",
		"Образование",
		#"Знание языков",
		"Повышение квалификации, курсы",
		"Тесты, экзамены",
		"Гражданство, время пути до работы",
		"Дополнительная информация",
		"Опыт вождения"
	]
	
	CURRENCIES = [
		"KZT",
		"RUB",
		"USD",
		"EUR"
	]
	
	def __init__(
		self, 
		name="",
		phones=[],
		emails=[],
		birth_date="", 
		gender="", 
		area="",
		citizenship="",
		ability_to_move_elsewhere="unknown",
		ability_to_go_for_business_trips="unknown",
		permission_to_work="",
		desired_position="", 
		specializations=[], 
		salary={"amount": 0, "currency": "KZT"}, 
		education_level="", 
		education=[], # {"year": 2020, "name": "", "organization": ""}
		languages=[], # {"name": "", "level": ""}
		experience=[], # {"start": "dd-MM-yyyy", "end": "dd-MM-yyyy", "position": "", "description": ""}
		additional_info="", # additional information 
		skill_set=[],
		seniority_level="",
		work_schedule=[],
		employment_type=[],
		desired_commute_time = ""
		):
		
		self.name = name # done
		self.phones = phones # done
		self.primary_phone = None # done
		self.emails = emails # done
		self.birth_date = birth_date # done
		self.gender = gender # done
		self.area = area # done
		self.desired_position = desired_position # done
		self.specializations = specializations # done
		self.salary = salary # done
		self.education_level = education_level # done
		self.education = education # done
		self.languages = languages 
		self.experience = experience # almost done (resolve the location issue with either ML or a list of locations)
		self.additional_info = additional_info
		self.skill_set = skill_set
		self.ability_to_move_elsewhere = ability_to_move_elsewhere # done
		self.ability_to_go_for_business_trips = ability_to_go_for_business_trips # done
		self.permission_to_work = permission_to_work # done
		self.citizenship = citizenship # done
		self.seniority_level = seniority_level # done
		self.work_schedule = work_schedule # done
		self.employment_type = employment_type # done
		self.desired_commute_time = desired_commute_time # done
		self.test_array = []
		
	def as_json(self):
		return json.dumps(
			{
				"name": self.name,
				"phones": self.phones,
				"primary phone": self.primary_phone,
				"emails": self.emails,
				"birth date": self.birth_date,
				"gender": self.gender,
				"area": self.area,
				"desired position": self.desired_position,
				"specializations": self.specializations,
				"salary": self.salary,
				"education_level": self.education_level,
				"education": self.education,
				"languages": self.languages,
				"experience": self.experience,
				"additional_info": self.additional_info,
				"skill set": self.skill_set,
				"ability to move elsewhere": self.ability_to_move_elsewhere,
				"ability to go for business trips": self.ability_to_go_for_business_trips,
				"permission to work": self.permission_to_work,
				"citizenship": self.citizenship,
				"seniority level": self.seniority_level,
				"work schedule": self.work_schedule,
				"employment type": self.employment_type,
				"desired commute time": self.desired_commute_time
			}, 
			indent=4, 
			ensure_ascii=False
		).encode("utf-8").decode()

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

def extract_html_elems(parsed_html, elems):
	with open(RESUME_IDS_FILENAME, "w", encoding="utf-8") as f:
		for elem in elems:
			data = parsed_html.body.findAll(elem[0], elem[1])
			for p in data:
				print(p.text, file=f)

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
		'svb','tc','template','themedata','desired_position','txe','ud','upr','userprops',
		'wgrffmtfilter','windowcaption','writereservation','writereservhash','xe','xform',
		'xmlattrname','xmlattrvalue','xmlclose','xmlname','xmlnstbl',
		'xmlopen',
	))
	# Translation of some special characters.
	specialchars = {
		'par': '\n',
		'pard': '\n',
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
			elif char == "@":
				if not ignorable:
					out.append(char)
		elif word: # \foo
			curskip = 0
			if word in destinations:
				ignorable = True
			elif ignorable:
				pass
			elif word in specialchars:
				out.append(specialchars[word])
				#print("found a special char: %s" % specialchars[word])
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

def extract_data(text, type):
	phone_regex = r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
	regex = {
		"phone": r'(\+?\d{1}\s?\(?\d{3}\)?\s?[-\.\s]??\d{3}[-\.\s]??\d{2}\s?\d{2}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})',
		"email": r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
		"salary": r'^\d{1,3}[,.\s]?\d{1,3}',
		"work interval": r'[a-zA-Zа-яА-Я]+\s(19|20)\d{2}\s?—\s?[a-zA-Zа-яА-Я\s]+(\s(19|20)\d{2})?' # r'[a-zA-Zа-яА-Я]+\s(19|20)\d{2}'
	}
	
	r = re.compile(regex[type])
	
	all = r.findall(text)
	return all

def strip_empty_lines(lines):
	stripped_lines = []
	for line in lines:
		if line.strip() != "":
			stripped_lines.append(line)
	return stripped_lines

def traverse_lines(r, lines):
	# lines[i] 1: name
	r.name = lines[0].strip()
	
	# some info may be missing, so look for individual words
	
	if "Мужчина" in lines[1]:
		r.gender = "Мужчина"
	elif "Женщина" in lines[1]:
		r.gender = "Женщина"
	
	if "родился" in lines[1]:
		r.birth_date = lines[1].split("родился")[1].strip()
	
	curr_section = None
	sections = {}
	
	for i in range(len(lines)):
		lines[i] = lines[i].strip()
		lc_line = lines[i].lower()
		
		# phone
		phone_matches = list(set(extract_data(lines[i], "phone")))
		if len(phone_matches) != 0:
			phone_matches = [p.replace(" ", "") for p in phone_matches]
			r.phones = r.phones + phone_matches
			if "предпочитаемый способ связи" in lines[i]:
				r.primary_phone = phone_matches[0]
		
		# email
		email_matches = list(set(extract_data(lines[i], "email")))
		if "k_dmitriy_v@outlook.com" in lines[i]:
			print(lines[i])
		if len(email_matches) != 0:
			email_matches = [x.replace(" ", "") for x in email_matches]
			print(email_matches)
			r.emails = r.emails + email_matches
		
		# area
		if "Проживает" in lines[i]:
			r.area = lines[i].split(":")[1].replace(" ", "")
		
		# citizenship and permission to work
		if "Гражданство" in lines[i]:
			parts = lines[i].split(",")
			r.citizenship = parts[0].split(":")[1].replace(" ", "")
			if len(parts) > 1:
				r.permission_to_work = parts[1].split(":")[1].replace(" ", "")
		
		if "переезд" in lc_line:
			parts = lines[i].split(",")
			r.ability_to_move_elsewhere = parts[0].lower().strip()
			if len(parts) > 1 and "командировка" in parts[1]:
				r.ability_to_go_for_business_trips = parts[1].lower().strip()
		
		#if "Желаемая должность и зарплата" in lines[i] and i + 1 < len(lines):
			#r.desired_position = lines[i + 1].strip()
		
		# extract sections and tackle them separately
		for section in HHResume.SECTION_NAMES:
			if section in lines[i] and section not in sections:
				curr_section = section
		
		if curr_section is not None:
			if not curr_section in sections:
				sections[curr_section] = []
			else:
				sections[curr_section].append(lines[i])
	
	print("SECTIONS:", sections)
	
	# tackle sections
	tackle_sections(r, sections)

def tackle_sections(r, sections):
	for section_name in sections:
		if section_name == "Желаемая должность и зарплата":
			# assume line 0 is always the name of the desired position
			r.desired_position = sections[section_name][0].strip()
			r.seniority_level = sections[section_name][1].strip()
			
			# specializations are all lines until "Занятость"
			for line in sections[section_name][2:]:
				if "•" in line:
					r.specializations.append(line.replace("•", "").strip())
				if "Занятость" in line:
					r.employment_type = [x.strip() for x in line.split(":")[1].split(",")]
				if "График работы" in line:
					r.work_schedule = [x.strip() for x in line.split(":")[1].split(",")]
				if "Желательное время в пути до работы" in line:
					r.desired_commute_time = line.split(":")[1].strip()
				
				# extract salary amount
				matches = extract_data(line, "salary")
				if len(matches) == 1:
					r.salary["amount"] = matches[0]
				
				# extract salary currency
				potential_salary_currency =  line.strip().upper()
				if potential_salary_currency in HHResume.CURRENCIES:
					r.salary["currency"] = potential_salary_currency
		
		if "Опыт работы" in section_name:
			# split by work intervals
			curr_work_interval = None
			jobs = {}
			
			for i in range(len(sections[section_name])):
				work_interval_matches = extract_data(sections[section_name][i], "work interval")
				#print("Work interval matches:", work_interval_matches)
				if len(work_interval_matches) > 0 or "— настоящее время" in sections[section_name][i]:
					curr_work_interval = sections[section_name][i]
				if curr_work_interval not in jobs:
					jobs[curr_work_interval] = []
				else:
					jobs[curr_work_interval].append(sections[section_name][i])
					
			for wi in jobs:
				lines = jobs[wi]
				work_exp = {}
				print([x.strip() for x in wi.split("—")])
				work_exp["start"], work_exp["end"] = [x.strip() for x in wi.split("—")]
				for i in range(len(lines)):
					curr_index = i
					curr_index = 1
					if curr_index < len(lines):
						work_exp["organization"] = lines[curr_index] 
						curr_index += 1
					
					if curr_index < len(lines) and len(lines) > 4:
						work_exp["location"] = lines[curr_index]
						curr_index += 1
					
					if curr_index < len(lines):
						work_exp["position"] = lines[curr_index] 
						curr_index += 1
					
					if curr_index < len(lines):
						work_exp["responsibilities"] = lines[curr_index]
						curr_index += 1
				r.experience.append(work_exp)

		if section_name == "Образование":
			# assume that there are 4 lines per education item
			print("EDUCATION:", sections[section_name])
			
			curr_index = 0
			if curr_index < len(sections[section_name]):
				r.education_level = sections[section_name][0]
				curr_index += 1
				
			while curr_index < len(sections[section_name]):
				edu_item = {}
				#if curr_index < len(sections[section_name]):
					#if r.education_level == "":
						#r.education_level = sections[section_name][curr_index]
					#edu_item["education level"] = sections[section_name][curr_index]
					#curr_index += 1
				
				if curr_index < len(sections[section_name]):

					edu_item["year"] = sections[section_name][curr_index]
					curr_index += 1
				
				if curr_index < len(sections[section_name]):
					edu_item["organization"] = sections[section_name][curr_index]
					curr_index += 1
				
				if curr_index < len(sections[section_name]):
					edu_item["description"] = "\n".join(sections[section_name][curr_index:])
					curr_index += 1
				
				r.education.append(edu_item)
		
		if section_name == "Ключевые навыки":
			# split into 2 sections: languages and skills
			sub_sections = {"Знание языков": [], "Навыки": []}
			curr_sub_section = None
			for i in range(len(sections[section_name])):
				if sections[section_name][i].strip() in sub_sections:
					curr_sub_section = sections[section_name][i].strip()
				else:
					sub_sections[curr_sub_section].append(sections[section_name][i]) 
			
			for l in sub_sections["Знание языков"]:
				temp = l.split("—")
				r.languages.append({"name": temp[0].strip(), "level": "—".join(temp[1:]).strip()})
		
		if section_name == "Дополнительная информация":
			r.additional_info = "\n".join(sections[section_name])

if __name__ == "__main__":
	prepare_dirs()
	
	# if not os.path.isfile(os.path.join(HTML_DIR, RESUME_LIST_HTML_FILENAME)):
		# html = download_resume_list("https://pavlodar.hh.kz/search/resume?text=%D1%8E%D1%80%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D1%8D%D0%BA%D0%BE%D0%BD%D0%BE%D0%BC%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%90%D0%BD%D0%B0%D0%BB%D0%B8%D1%82%D0%B8%D0%BA&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%94%D0%B8%D0%B7%D0%B0%D0%B9%D0%BD%D0%B5%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%94%D0%B8%D1%80%D0%B5%D0%BA%D1%82%D0%BE%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%A0%D1%83%D0%BA%D0%BE%D0%B2%D0%BE%D0%B4%D0%B8%D1%82%D0%B5%D0%BB%D1%8C&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%96%D1%83%D1%80%D0%BD%D0%B0%D0%BB%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9F%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9C%D0%B0%D1%80%D0%BA%D0%B5%D1%82%D0%BE%D0%BB%D0%BE%D0%B3&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%91%D1%83%D1%85%D0%B3%D0%B0%D0%BB%D1%82%D0%B5%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=HR&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%A4%D0%B8%D0%BD%D0%B0%D0%BD%D1%81%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%91%D0%B0%D0%BD%D0%BA&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%93%D0%B5%D0%BE%D0%B4%D0%B5%D0%B7%D0%B8%D1%81%D1%82&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&text=%D0%9F%D0%BE%D0%B2%D0%B0%D1%80&st=resumeSearch&logic=except&pos=full_text&exp_period=all_time&exp_company_size=any&exp_industry=any&area=160&relocation=living_or_relocation&salary_from=&salary_to=120000&currency_code=KZT&education=none&age_from=18&age_to=45&gender=male&employment=full&schedule=fullDay&order_by=publication_time&search_period=30&items_on_page=100&no_magic=false")
	# else:
		# with open(get_resume_list_html_path(), "r", encoding="utf-8") as f:
			# html = f.read()
	
	
	# if not os.path.isfile(RESUME_IDS_FILENAME):
		# extract_resume_ids(html, elems)
	
	# # extract resume IDs
	# #with open(RESUME_IDS_FILENAME, "r") as f:
		# #resume_ids = [x.replace("\n", "") for x in f.readlines()]
	
	# # extract name, phone, etc.
	# parsed_html = BeautifulSoup(html, features="lxml")
	# elems = [
		# ("div", {"class": "resume-search-item__fullname"}), # full name
		# ("span", {"data-qa": "resume-serp__resume-age"}), # age
		# ("div", {"data-qa": "resume-serp__resume-excpirience-sum"}), # experience
		# ("div", {"data-hh-last-experience-id": re.compile(r".*")}),
		# ("div", {"resume-search-item__company-name": re.compile(r".*")})
	# ]
	
	# elems = [
		# ("div", {"data-qa": "resume-serp__resume"})
	# ]
	
	#extract_data(parsed_html, elems)
	
	resumes = []
	
	for file in os.listdir("resume"):
		if file.split(".")[1] == "doc" and not "$" in file:
			print("Traversing {0}".format(file))
			r = HHResume()
			r.specializations = []
			r.experience = []
			r.education = []
			#print(r.as_json())
			with open("resume/" + file, "r") as f:
				
				# convert rtf string to text and extract email from raw rtf string
				rtf_str = f.read().replace(u'\xa0', u' ')
				
				r.emails = list(set(extract_data(rtf_str, "email")))
				
				text = striprtf(rtf_str)
				text = unicodedata.normalize("NFKD", text).replace("\\xa0", u" ").replace("\\xA0", u" ").replace('\xa0', u' ').replace('\xA0', u' ').replace(u'\xa0', u' ').replace(u'\xA0', u' ')
				# strip empty lines
				lines = strip_empty_lines(text.split("\n"))
				traverse_lines(r, lines)
				#new_str = unicodedata.normalize("NFKD", r.as_json())#.replace("\\xa0", u" ").replace("\\xA0", u" ").replace('\xa0', u' ').replace('\xA0', u' ').replace(u'\xa0', u' ').replace(u'\xA0', u' ')
				#print("json/" + file.split(".")[0] + ".json")
				with open("json/" + file.split(".")[0] + ".json", "w", encoding="utf-8") as json_file:
					print(r.as_json(), file=json_file)
				#print(new_str)
			r.test_array.append(file)
			print("Specializations: {0}".format(r.specializations))
			print("Test array: {0}".format(r.test_array))
			r = None
	
	
	#for ri in resume_ids[:1]:
		#resume = download.resume(ri)
		#with open(os.path.join(JSON_DIR, ri + ".json"), "w") as f:
			#resume = parse.resume(resume)
			#f.write(json.dumps(resume, ensure_ascii=False))
	