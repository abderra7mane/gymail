#!/usr/bin/env python
#-*- coding: utf-8 -*-



from email.header import decode_header
from base64 import b64decode




def parse_msg (msg) :
	
	headers = {}
	
	text = ''
	
	attachments = []
	
	
	headers['subject'] =  decode_header(msg['subject'])[0][0]
	headers['from']    =  decode_header(msg['from'])[0][0]
	headers['to']      =  decode_header(msg['to'])[0][0]
	headers['cc']      =  decode_header(msg['cc'])[0][0]

	
	payload = msg.get_payload()


	if msg.is_multipart() :
	
		for m in payload :

			_, txt, attch = parse_msg(m)
		
			text += txt

			attachments.extend(attch)


	else:

		content_type = msg.get_content_type()


		if content_type == 'text/plain' :

			text += msg.get_payload()


		elif content_type == 'text/html' :

			pass


		else :

			filename = msg.get_filename()


			if filename :	

				payload = b64decode(payload)
				
				attachments.append((filename, payload))


	return headers, text, attachments
	
	
