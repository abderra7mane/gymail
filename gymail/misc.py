#!/usr/bin/env python
#-*- coding: utf-8 -*-




import sys
import os





def is_sequence (obj) :
	
	return hasattr(obj, '__iter__')




def debug (msg='', out=sys.stdout) :

	print >>out, msg




def yes_no_question (qstr, custom=False) :
		
	if custom :
		
		qstr = "{qstr} [yes/no/custom] ".format(qstr=qstr)
		
		
	else :
		
		qstr = "{qstr} [yes/no] ".format(qstr=qstr)
	
	
	response = raw_input(qstr).strip().lower()
	
	
	if custom and (len(response) == 0 or response in 'custom') :
		
		return None
		
	
	elif response in 'yes' :
		
		return True
		
	
	else :
		
		return False




def get_path (default=os.getcwd()) :
	
	path = ''
	

	while not os.path.isdir(path) :
		
		path = raw_input("Enter a target path ({default}) : ".format(default=default)).strip()
		
		
		if len(path) == 0 :
			
			path = default
		
	
	return path


