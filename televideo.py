# -*- coding: utf-8 -*-
import feedparser
import urllib
import json
import telegram
from telegram.error import NetworkError, Unauthorized
import time
import datetime

weekdays = ["Lunedì","Martedì","Mercoledì","Giovedì","Venerdì","Sabato","Domenica"]
months = ["Gennaio","Febbraio","Marzo","Aprile","Maggio","Giugno","Luglio","Agosto","Settembre","Ottobre","Novembre","Dicembre"]

TOKEN_TELEGRAM = '322540065:AAG1oe2RO1FaOnaqt6CSN6mK92twcq9fbzA' #altre rss
MY_CHAT_ID = 31923577
bot = telegram.Bot(TOKEN_TELEGRAM)
previous_title = 0

def RSS():
	global previous_title
	feed = feedparser.parse(	"http://www.servizitelevideo.rai.it/televideo/pub/rss101.xml"	)
	title = feed.entries[0].title.encode('utf-8')
	description = feed.entries[0].description.encode('utf-8')
	#print description
	if title != previous_title:
		previous_title = title
		oggi = datetime.datetime.today()
		nomeGiorno = weekdays[	oggi.weekday() ]
		nomeMese = months[	oggi.month - 1 ]
		anno = oggi.year
		nGiorno = oggi.day
		ora = str(oggi.hour) + ":" + str(oggi.minute)
		TITOLO = "<strong>" + title.encode('utf-8') + "</strong>"
		DATA =  "\n<i>" + ora + " " + nomeGiorno + " " + str(nGiorno) + " " + nomeMese + " " + str(anno) + "</i>"
		ARTICOLO = " ".join(	description.split(" ")[1:]	)
		text = TITOLO + DATA 
		#bot.sendPhoto(chat_id = MY_CHAT_ID, photo = "http://www.servizitelevideo.rai.it/televideo/pub/tt4web/Nazionale/16_9_page-103.png")
		bot.sendMessage(chat_id = MY_CHAT_ID,text=text, parse_mode="Html", disable_web_page_preview=True)
	
def echo():
	RSS()

while True:
	try:
		echo()
		time.sleep(10)
	except NetworkError:
		time.sleep(1)
	except Unauthorized:
		update_id += 1
