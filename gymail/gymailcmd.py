#!/usr/bin/env python
#-*- coding: utf-8 -*-



import cmd
import sys
import os
import os.path

from email.parser import Parser

from conn import *
from mail import *
from message import *
from misc import *
from consts import *






class GymailCmd (cmd.Cmd) :

	"""
Gymail command line tool main class.
	"""


	prompt = '\033[1;31m(gymail)\033[0m|#> '


	user_configuration = {
		'username' :  None,
		'password' :  None,
	}


	is_connected = False
	is_logged_in = False


	session = None
	mailbox = None
	
	
	attachments = []



	def do_set (self, args='') :
		
		"""
Set/Clear application configurations.

	\033[1mUsage:\033[0m set <option> [<value>]

	options :  
		username
		password

	\033[1mNote:\033[0m Leave the value empty to clear the option.
		"""


		retcode, list_args = self.parse_args(args, [1, 2])

		
		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return

		
		if len(list_args) == 1 :
			
			list_args.append(None)
		
		
		option, value = list_args

		
		if not self.user_configuration.has_key(option) :
			
			debug(INVALID_OPTION)
			
			return

		
		self.user_configuration[option] = value




	def do_get (self, args='') :
		
		"""
Query application configurations.

	\033[1mUsage:\033[0m get <option>

	options :  
		username
		password
		"""


		retcode, list_args = self.parse_args(args, 1)


		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		option =  list_args[0]


		if not self.user_configuration.has_key(option) :
			
			debug(INVALID_OPTION)
			
			return


		if option == 'password' :
			
			response = yes_no_question("Make sure that you are alone, continue?", True)
			

			if response != True :
				
				return


		value  =  self.user_configuration[option]
		

		if value == None :
			
			value = 'n/a'

			
		debug("[?] {option} :  {value}".format(option=option.title(), value=value))




	def do_connect (self, args='') :
		
		"""
Initiate connection to mail server.

	\033[1mUsage:\033[0m connect
		"""


		retcode, _ = self.parse_args(args, 0)


		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		if self.is_connected:
			
			debug(ALREADY_CONNECTED)
			
			return


		self.is_connected, self.session = connect()


		if self.is_connected :
			
			debug(SESSION_INIT_SUCCESS)




	def do_login (self, args='') :
		
		"""
Login to mail server.

	\033[1mUsage:\033[0m login [<username>]
		"""


		retcode, list_args = self.parse_args(args, [0, 1])


		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		if self.is_logged_in:
			
			debug(ALREADY_LOGGED_IN)
			
			return
			
		
		if len(list_args) == 1 :
			
			self.user_configuration['username'] = list_args[0]


		username, password = get_cridentials(
			self.user_configuration['username'],
			self.user_configuration['password'],
		)


		if not self.is_connected :
			
			self.do_connect()


		self.is_logged_in = login(self.session, username, password)


		if self.is_logged_in :
			
			debug(AUTHENTICATION_SUCCESS)
			
			debug(LOGGED_IN)
			
			self.mailbox = None
			
		else :
			
			debug(AUTHENTICATION_FAILED)




	def do_logout (self, args='') :
		
		"""
Logout from mail server.

	\033[1mUsage:\033[0m logout
		"""


		retcode, _ = self.parse_args(args, 0)


		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		if not self.is_logged_in :
			
			debug(NOT_ALREADY_LOGGED_IN)
			
			return


		self.is_connected = self.is_logged_in = logout(self.session)


		self.mailbox = None


		debug(LOGGED_OUT)
	



	def do_status (self, args='') :
		
		"""
Query the status of a mailbox.

	\033[1mUsage:\033[0m status [<mailbox> [<flag>]]

	mailbox :           (default: selected using `select` or inbox)
		inbox
		all_mail
		drafts
		sent_mail
		important
		starred
		spam
		trash

	flag :              (default: all)
		all
		unseen
		"""


		retcode, list_args = self.parse_args(args, [0, 1, 2])
		

		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		if len(list_args) == 0 :
			
			if self.mailbox != None :
				
				list_args.append(self.mailbox)
			
			else:
				
				list_args.append('inbox')


		if len(list_args) == 1 :
			
			list_args.append('all')
		
		
		mailbox, flag = list_args


		if not mailboxs_bindings.has_key(mailbox) :
			
			debug(INVALID_MAILBOX)
			
			return


		if flag not in ('all', 'unseen') :
			
			debug(INVALID_FLAG)
			
			return


		if not self.is_logged_in :
			
			debug(NOT_ALREADY_LOGGED_IN)
			
			return

		
		self.mailbox, emails_ids = search(self.session, mailbox, flag)		
		
		emails_count = len(emails_ids)
		
		mailbox = mailbox.replace('_', ' ').title()


		if flag == 'all' :

			if emails_count > 0 :
				
				debug("[?] you have {emails_count} email(s) in '{mailbox}'.".format(
					emails_count =  emails_count, 
					mailbox      =  mailbox
				))

			else :
				
				debug("[?] you have no emails in {mailbox}.".format(mailbox = mailbox))


		elif flag == 'unseen' :

			if emails_count > 0 :

				debug("[?] you have {emails_count} new email(s) in {mailbox}.".format(
					emails_count =  emails_count,
					mailbox      =  mailbox
				))

			else :
				
				debug("[?] you have no new emails in {mailbox}".format(mailbox = mailbox))




	def do_list (self, args='') :

		"""
List the content of a mailbox.

	\033[1mUsage:\033[0m list [<mailbox> [<flag>]]

	mailbox :           (default: selected using `select` or inbox)
		inbox
		all_mail
		drafts
		sent_mail
		important
		starred
		spam
		trash

	flag :              (default: all)
		all
		unseen
		"""


		retcode, list_args = self.parse_args(args, [0, 1, 2])


		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return


		if len(list_args) == 0 :
			
			if self.mailbox != None :
				
				list_args.append(self.mailbox)
			
			else:
				
				list_args.append('inbox')


		if len(list_args) == 1 :
			
			list_args.append('all')
		
		
		mailbox, flag = list_args


		if not mailboxs_bindings.has_key(mailbox) :
			
			debug(INVALID_MAILBOX)
			
			return


		if flag not in ('all', 'unseen') :
			
			debug(INVALID_FLAG)
			
			return


		if not self.is_logged_in :
			
			debug(NOT_ALREADY_LOGGED_IN)
			
			return


		self.mailbox, email_ids = search(self.session, mailbox, flag)


		debug()


		for email_id in email_ids :
			
				subject, from_, email_size = email_info(self.session, email_id)


				debug("({id_}).\tSubject :  {subject}".format(id_=email_id, subject=subject))
				
				debug(        "\tFrom    :  {from_}".format(from_=from_))
				
				debug(        "\tSize    :  {size} Bytes".format(size=email_size))
				
				debug()




	def do_select (self, args='') :
		
		"""
Select a mailbox.

	\033[1mUsage:\033[0m select [<mailbox>]

	mailbox :
		inbox           (default)
		all_mail
		drafts
		sent_mail
		important
		starred
		spam
		trash
		"""


		retcode, list_args = self.parse_args(args, [0, 1])
		

		if retcode == False :
		
			debug(INVALID_ARGS_COUNT)
		
			return


		if len(list_args) == 0 :

			list_args.append('inbox')


		mailbox = list_args[0]


		if not mailboxs_bindings.has_key(mailbox) :

			debug(INVALID_MAILBOX)

			return


		if not self.is_logged_in :

			debug(NOT_ALREADY_LOGGED_IN)

			return


		retcode, response = self.session.select(mailboxs_bindings[mailbox])


		if retcode == 'OK' :

			print "[+] mailbox '{mailbox}' selected :(".format(
				mailbox = mailbox.replace('_', ' ').title()
			)

			self.mailbox = mailbox




	def do_fetch (self, args='') :
		
		"""
Fetch the content of an email.

	\033[1mUsage:\033[0m fetch <email_id>

	\033[1mNote:\033[0m Usally from 1 to <email_count>
	      Use command `list` to be more accurate.
		"""

		
		retcode, list_args = self.parse_args(args, 1)


		if retcode == False :

			debug(INVALID_ARGS_COUNT)

			return


		if not self.is_logged_in :

			debug(NOT_ALREADY_LOGGED_IN)

			return


		if self.mailbox == None :

			debug(NO_INBOX_SELECTED)

			return


		email_id = int(list_args[0])

		content = fetch(self.session, email_id)


		if content == None :

			debug(NO_DATA_RECEIVED)

			return
			
			
		headers, text, attachments = self.parse_email(content)
		
		
		self.debug_email(email_id, headers, text, attachments)
		
		
		self.attachments = attachments
		
		
		if len(self.attachments) > 0 :
			
			debug(ATTACHMENTS_AVAILABLE)
		
		
		
		
	def do_attach (self, args='') :
		
		"""
List attachments from last fetched email.

	\033[1mUsage:\033[0m attach

	\033[1mNote:\033[0m See command `save` to save attachments content.
		"""
		
		
		retcode, _ = self.parse_args(args, 0)
		
		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return
			
		
		if len(self.attachments) == 0 :
			
			debug(NO_ATTACHMENTS)
			
			return
			
			
		for i in range(len(self.attachments)) :
			
			id_ = i
			
			filename = self.attachments[i][0]
			
			size = len(self.attachments[i][1])
			
			
			self.debug_attachment(id_, filename, size)
		
		
		
		
	def do_save (self, args='') :
		
		"""
Save attachments content from last fetched email.

	\033[1mUsage:\033[0m save [<attachment_id>]

	\033[1mNote:\033[0m See command `attach` to get attachment id.
	      Leave argument field empty to save all attachments.
		"""
		
		
		retcode, list_args = self.parse_args(args, [0, 1])
		
		
		if retcode == False :
			
			debug(INVALID_ARGS_COUNT)
			
			return
			
		
		if len(self.attachments) == 0 :
			
			debug(NO_ATTACHMENTS)
			
			return
			
		
		all_ids = range(len(self.attachments))
			
			
		if len(list_args) == 0 :
			
			list_ids = all_ids

			
		else :
			
			id_ = int(list_args[0])
			
			
			if id_ not in all_ids :
				
				debug(INVALID_ATTACH_ID)
				
				return
				
			
			list_ids = [id_]


		path = get_path()
			
		
		for id_ in list_ids :
			
			filename, content = self.attachments[id_]
			
			file_path = os.path.join(path, filename)
			
			
			open(file_path, 'wb').write(content)




	def do_noop (self, args='') :
		
		"""
Send a noop command to mail server.

	\033[1mUsage:\033[0m noop

	\033[1mNote:\033[0m Used to keep connection alive.
		"""


		if self.is_logged_in :

			noop(self.session)




	def do_exit (self, args='') :
		
		"""
Exit the application.
	
	\033[1mUsage:\033[0m exit
		"""


		if self.is_logged_in :
			
			self.do_logout()


		sys.exit(0)




	do_quit = do_exit




	def emptyline (self) :
		
		"""
Empty line command.
		"""
		
		
		pass




	def parse_args (self, args, count) :
		
		"""
Parse arguments given as one line.

	count : number of arguments
	        integer for fixed number, or a list of 
	        of possible values.
		"""
		
		args = args.lower().strip().split()


		if is_sequence(count) :
			
			valid = len(args) in count
			
		else :
			
			valid = len(args) == count

			
		return valid, args




	def debug_headers (self, headers) :
		
		"""
Print email important headers.
		"""
		
		
		pass




	def parse_email (self, content) :
		
		"""
Parse the content of an email returned
by IMAP server as specified in RFC822.
		"""
		
		
		message = Parser().parsestr(content)
		
		
		return parse_msg(message)




	def debug_email (self, email_id, headers, text, attachments) :
		
		"""
Print infos about emails.
		"""
		
		
		debug()
		
		debug("(%s).\tSubject    :  %s"  %  (email_id, headers['subject']))
		
		debug(     "\tFrom       :  %s"  %  (headers['from']))
		
		debug(     "\tTo         :  %s"  %  (headers['to']))
		
		debug(     "\tCC         :  %s"  %  (headers['cc']))
		
		
		for (file_name, file_content) in attachments :
			
			debug( "\tAttachment :  %s (%d B)"    %  (file_name, len(file_content)))


		debug(     "\tContent    :  (%d B)\n\n%s" %  (len(text), text))
		
		debug()




	def debug_attachment (self, id_, filename, size) :
		
		"""
Print infos about attachments.
		"""
		
		debug()
		
		debug("({id_}).\tFile Name :  {filename}".format(id_=id_, filename=filename))
		
		debug(        "\tSize      :  {size} B".format(size=size))
		
		debug()



