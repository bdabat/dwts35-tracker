"""Conservative update: only accept explicit ABC News weekly elimination entries.
Runs in GitHub Actions. If source structure changes, preserve last verified data.
"""
import json,re,datetime,pathlib,requests
from bs4 import BeautifulSoup
P=pathlib.Path(__file__).parent/'results.json'
URL='https://abcnews.com/amp/GMA/Culture/dancing-with-the-stars-season-35-who-is-eliminated/story?id=136377567'
KNOWN=['Amber Glenn','Ciara Miller','Conner Leavitt','Connor Wood','Ezra Frech','Giada De Laurentiis','Guillermo Rodriguez','Harry Shum Jr.','Jackson Olson','Jenna Dewan','Julia Stiles','Maura Higgins','Sarah Jane Nader','Tatyana Ali','Taylor Hanson','Tyler Cameron']
old=json.loads(P.read_text()); html=requests.get(URL,timeout=25,headers={'User-Agent':'Mozilla/5.0'});html.raise_for_status();soup=BeautifulSoup(html.text,'html.parser')
text=soup.get_text(' ',strip=True)
# Isolate the elimination section; avoid classifying mentions elsewhere as eliminations.
match=re.search(r'Who has been eliminated from.*?season 35\?',text,re.I)
end=re.search(r'Who is still on.*?season 35\?',text,re.I)
if not match or not end or end.start()<=match.end():raise SystemExit('Cannot reliably parse elimination section; keeping existing results')
segment=text[match.end():end.start()]
# Find explicit "NAME and ... eliminated" / "NAME ... were eliminated" within a short span.
confirmed=set(old['eliminated'])
for name in KNOWN:
 for m in re.finditer(re.escape(name),segment,re.I):
  tail=segment[m.end():m.end()+230]
  if re.search(r'\b(eliminated|sent home|went home)\b',tail,re.I) and not re.search(r'\b(not|no one|nobody)\b.{0,25}\beliminated\b',tail,re.I):confirmed.add(name)
# Never accept more than 2 new eliminations per check; avoid parsing errors.
if len(confirmed-set(old['eliminated']))>2:raise SystemExit('Unexpected number of eliminations; keeping existing results')
if len(confirmed)>len(old['eliminated']):
 old['eliminated']=[n for n in KNOWN if n in confirmed]
 old['updated']=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y-%m-%d %H:%M ET')
 old['note']='Eliminations updated from ABC News. Scores may reflect the previous verified episode.'
 P.write_text(json.dumps(old,indent=2)+'\n')
 print('Updated:',old['eliminated'])
else:print('No new verified eliminations')
