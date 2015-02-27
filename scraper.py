from __future__ import division
# This is a template for a Python scraper on Morph (https://morph.io)
# including some code snippets below that you should find helpful

constituencyslugs=['isle-of-wight']

nodrop=0

import scraperwiki

import requests
import datetime
from bs4 import BeautifulSoup

def dropper(table):
    """ Helper function to drop a table """
    if nodrop==1: return
    print "dropping",table
    if table!='':
        try: scraperwiki.sqlite.execute('drop table "'+table+'"')
        except: pass
        
def urlbuilder_constituency(constslug):
  return 'http://www.oddschecker.com/politics/british-politics/{0}/winning-party'.format(constslug)

def makeSoup(url):
	try:
		r = requests.get(url)
		#print '>>>',r.history
		ret= BeautifulSoup(r.text)
		for s in r.history:
			if s.status_code==302: ret==""
	except: ret=""
	return ret

def oddsGrabber(soup,default):
  if soup=="": return {}
  #soup=makeSoup(url)
  table=soup.find( "tbody", {"id":"t1"} )
  allbets=default
  allbets['time']=datetime.datetime.utcnow()
  bets={}
  for row in table.findAll('tr'):
    name=row('td')[1].string
    tds = row('td')[3:]
    bets[name]={}
    for td in tds:
      if td.string!=None:
        try:
          bets[name][ td['id'].split('_')[1] ]=td.string
        except: pass
  allbets['odds']=bets
  return allbets

def oddsGrabber_constituency(constslug,default):
  url=urlbuilder_constituency(constslug)
  soup=makeSoup(url)
  if soup=='':
    return {}
  return oddsGrabber(soup,default)

def oddsParser(odds):
  bigodds=[]
  oddsdata=odds['odds']
  for party in oddsdata:
    #data in tidy format
    data={'time':odds['time'],'constituency':odds['const']}
    for bookie in oddsdata[party]:
      data['party']=party
      data['bookie']=bookie
      data['oddsraw']=oddsdata[party][bookie]
      data['odds']=eval(data['oddsraw'])
    bigodds.append(data.copy()) 
  return bigodds

typ='constituency2015GE'
dropper(typ)

dropper('UKconst2015')
dropper('constituency2015GE')
dropper('data')
	
for const in constituencyslugs:
  odds=oddsGrabber_constituency(const,{'typ':typ,'const':const})
  oddsdata=oddsParser(odds)
  scraperwiki.sqlite.save(table_name=typ, data=oddsdata)

# import lxml.html
#
# # Read in a page
# html = scraperwiki.scrape("http://foo.com")
#
# # Find something on the page using css selectors
# root = lxml.html.fromstring(html)
# root.cssselect("div[align='left']")
#
# # Write out to the sqlite database using scraperwiki library
# scraperwiki.sqlite.save(unique_keys=['name'], data={"name": "susan", "occupation": "software developer"})
#
# # An arbitrary query against the database
# scraperwiki.sql.select("* from data where 'name'='peter'")

# You don't have to do things with the ScraperWiki and lxml libraries. You can use whatever libraries are installed
# on Morph for Python (https://github.com/openaustralia/morph-docker-python/blob/master/pip_requirements.txt) and all that matters
# is that your final data is written to an Sqlite database called data.sqlite in the current working directory which
# has at least a table called data.
