# Jeff Stern, dedicated to Cait Holman
# Scrapes http://apod.nasa.gov/apod/ and downloads all photos

from bs4 import BeautifulSoup
from urllib import FancyURLopener

import urllib2
import os
import re
import csv
import sys
import datetime
import time
from dateutil import parser
from datetime import date, timedelta

reload(sys)
sys.setdefaultencoding('utf-8')

def parse_html(url):
	req = urllib2.Request(url)
	response = urllib2.urlopen(req)
	content = response.read()
	return BeautifulSoup(content, "html.parser")

def get_current_date_string():
	return datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")

def get_images(site):
	media = site.find("div","media")
	images = []
	if media:
		images = media.find_all("img")
		photoset = media.find("iframe","photoset")
		if photoset:
			photosetPage = parse_html(photoset['src'])
			images = images + photosetPage.find_all("img")
	return images

def get_copy(site):
	return site.find("div","copy")

def convert_to_plain_text(copy):
	return copy.text

def get_all_attr(elementList, attr):
	return [a[attr] for a in elementList]

def get_tags(site):
	tags = site.find("dl","tags")
	if tags:
		return [a.text for a in tags.find_all("a")]
	else:
		return []

def download_photo(img_url, filename):
	# http://stackoverflow.com/questions/3042757/downloading-a-picture-via-urllib-and-python
	try:
	    image_on_web = urllib2.urlopen(img_url)
	    if image_on_web.headers.maintype == 'image':
	        buf = image_on_web.read()
	        path = os.getcwd() + "/"
	        file_path = "%s%s" % (path, filename)
	        downloaded_image = file(file_path, "wb")
	        downloaded_image.write(buf)
	        downloaded_image.close()
	        image_on_web.close()
	    else:
			return False    
	except:
		print("URL for "+ img_url + " not found")
		return False
	return True

def convert_to_datetime(timestampString):
	today = date.today()
	yesterday = date.today() - timedelta(1)
	timestampString = timestampString.replace("Today", today.strftime('%b %d, %Y')).replace("Yesterday", yesterday.strftime('%b %d, %Y'))
	timestampString = timestampString.replace("March","Mar").replace("Sept","Sep").replace("June","Jun").replace("July","Jul").replace("April","Apr")
	datetime = parser.parse(timestampString)
	return datetime


## CREATING THREADS TABLE
f = open("threads.csv","wb")
output = csv.writer(f)

site = parse_html("https://scratch.mit.edu/discuss/10/?page=1")
totalPages = int(site.find_all("a","page")[-1].text)
for i in range(1,totalPages+1):
	site = parse_html("https://scratch.mit.edu/discuss/10/?page="+str(i))
	threads = site.find_all("tr")
	currentIter = 0
	for thread in threads[1:]:
		link = thread.find("h3","topic_isread").find("a").attrs["href"]
		title = thread.find("h3","topic_isread").find("a").text
		user = thread.find("span","byuser").text[3:]
		replies = site.find_all("td","tc2")[currentIter].text
		views = site.find_all("td","tc3")[currentIter].text
		lr =  site.find_all("td","tcr")[currentIter]
		lastresponse = convert_to_datetime(lr.find("a").text)
		lastresponder = lr.find("span","byuser").text[3:]
		data = [link,title,user,replies,views,lastresponse,lastresponder]
		output.writerow([unicode(s).encode("utf-8") for s in data])
		currentIter += 1
	print(i)

f.close()


## CREATING POSTS TABLE

threads = []
with open('threads.csv', 'rb') as f:
    reader = csv.reader(f)
    for row in reader:
    	threads.append(row[0])

f = open("posts.csv", "wb")
output = csv.writer(f)
for thread in threads[i:i+endRow]:
	threadURL = "https://scratch.mit.edu" + thread + "?page="
	pageNumber = 1
	totalPages = 1
	site = parse_html("https://scratch.mit.edu" + thread + "?page=1")
	pageList = site.find_all("a","page")
	if (len(pageList)>0):
		totalPages = int(site.find_all("a","page")[-1].text)
	while pageNumber <= totalPages:
		if pageNumber != 1:
			site = parse_html("https://scratch.mit.edu" + thread + "?page="+ str(pageNumber))

		posts = site.find_all("div","firstpost")
		
		for post in posts:
			postID = int(post["id"][1:])		# Get Post ID
			postNumber = int(post.find("span","conr").text.replace("#","")) # Post Number
 			timestamp =  post.find("div","box-head").find("a").text # Timestamp
 			timestamp = convert_to_datetime(timestamp)
 			content = post.find("div","post_body_html")
 			contentNoHTML = content.text # Post Content - No HTML
 			contentHTML = str(content)[28:-6] # Post Content - HTML
 			user = post.find('a','username').text # User
 			postcount = re.sub("[\t\n ]","",post.find('div','postleft').text.replace("Scratcher","").replace(user,""))  # User Post Count
			editedMessage = post.find("em","posteditmessage")
			edited = True if editedMessage else False # Was Edited?
			editDate = convert_to_datetime(editedMessage.text[editedMessage.text.rfind("(")+1:-1]) if edited else "" # Timestamp of edit
 			# Post Signature
 			signature = post.find("div","postsignature")
 			signatureNoHTML =  signature.text if signature else ""
 			signatureHTML = str(signature)[27:-6] if signature else ""
			data = [thread, postID, postNumber, timestamp, contentNoHTML, contentHTML, user, postcount, edited, editDate, signatureNoHTML, signatureHTML]
			output.writerow([unicode(s).encode("utf-8") for s in data])
			print(thread + " " + str(postNumber))
		pageNumber += 1

f.close()