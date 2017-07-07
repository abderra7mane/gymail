#!/usr/bin/env python
#-*- coding: utf-8 -*-




from email.header import decode_header

from consts import *




def noop (session) :
	
	session.noop()



def fetch (session, email_id) :

	retcode, response = session.fetch(email_id, '(RFC822)')
	
	
	content = response[0][1]

	return content
	
	

def select (session, mailbox) :
	
	session.select(mailboxs_bindings[mailbox])
	
	return mailbox



def search (session, mailbox, flag) :
	
	select(session, mailbox)
	
	_, response = session.search(None, '(%s)' % flag.upper())
	
	return mailbox, response[0].split()



def email_info (session, email_id) :
	
	retcode, response = session.fetch(
		email_id, '(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)] RFC822.SIZE)'
	)


	response_headers = response[0][0].split()

	size_idx         = response_headers.index('(RFC822.SIZE') + 1

	email_size       = int(response_headers[size_idx])


	response_body    = response[0][1].strip('\r\n').split('\r\n')


	for element in response_body :

		if element.startswith('From') :

			from_ = decode_header(element[6:])[0][0]
		
			try:
				idx = from_.rindex(' ')

				name_  = decode_header(from_[:idx].strip('"'))[0][0]

				email_ = decode_header(from_[idx+1:].strip('<>'))[0][0]

				from_ = "%s (%s)" % (name_, email_)

			except : pass


		elif element.startswith('Subject') :

			subject = decode_header(element[9:])[0][0]
			
	
	return subject, from_, email_size


