#!/usr/bin/env python
#-*- coding: utf-8 -*-



import imaplib
import getpass





IMAP_HOST = 'imap.gmail.com'
IMAP_PORT = 993





def connect () :

	session = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)

	return True, session



def login (session, username, password) :

	try:
		session.login(username, password)
		
		return True

	except imaplib.IMAP4.error :
		
		return False



def get_cridentials (username=None, password=None) :

	if username == None :
		
		username = raw_input("Enter Username : ")


	if password == None :
		
		password = getpass.getpass("Enter Password : ")


	return username, password



def logout (session) :

	session.logout()

	return False
	

