#coding: UTF-8
import re, json, subprocess, gammu

from slackbot.bot import respond_to

def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.read()
    
def placeCall(number, line):
	if number == '':
		reply = "Sorry, it seems that I lost track of the recipient."
	else:
		if number.startswith('+'): 
			number = '00'+number[1:]
		if line == 'landline':
			reply = "I'm trying to connect you."
			runProcess(["asterisk", "-rx", "channel originate sip/999 extension %(number)s@outbound-allroutes" % {'number': number}])
		elif line == 'gsm':
			reply = "I'm trying to connect you."
			runProcess(["asterisk", "-rx", "channel originate sip/999 extension %(number)s@outbound-gsm" % {'number': number}])
		else:
			reply = "Sorry, it seems that I lost track of the recipient."
	return(reply)

def findLastCall(listMessages):
	for m in listMessages:
		if 'attachments' in m: 
			if ('title' in m['attachments'][0]) and ('footer' in m['attachments'][0]):
				return m['attachments'][0]

@respond_to('help', re.IGNORECASE)
def help(message):
	help_message=" :wave: :robot_face: Hello! I'm @<SLACK_BOT>, a slackbot for talking with your personal Asterisk server easily. Here's how I work: \n\n"+\
            "  _Basic Commands:_  \n" +\
            "  `@<SLACK_BOT> call <number>` -- asks you what line to use to place the call.  \n" +\
            "  `@<SLACK_BOT> send message to <number>` -- asks what message to send to the specified phone number. Answer in a thread.  \n" +\
            "  `@<SLACK_BOT> call back` -- As a threaded reply to a notification, calls back the caller or the sender of a text message. Otherwise finds the latest possible correspondant in the conversation and places the call.  \n" +\
            "  _Advanced Commands:_  \n" +\
            "  `@<SLACK_BOT> get gsm status` -- asks about the status of the GSM line and returns the output.  \n" +\
            "  `@<SLACK_BOT> ask <request>` -- executes a request to Asterisk CLI and returns the output.  \n\n" +\
            "  Give me a try! :simple_smile: \n"
	if 'thread_ts' in message.body:
		pass
	else:
		message.reply(help_message)

@respond_to('ask (.*)', re.IGNORECASE)
def asteriskRequest(message, request):
	rawOutput = runProcess(["asterisk", "-rx", request])
	outputLines = rawOutput.splitlines()
	output = ""
	for line in outputLines:
		output += "`"+line+"` \n"
	if 'thread_ts' in message.body:
		pass
	else:
		message.reply(output)

@respond_to('get gsm status', re.IGNORECASE)
def dongleStatusRequest(message):
	rawOutput = runProcess(["asterisk", "-rx", "dongle show device state dongle0"])
	outputLines = rawOutput.splitlines()
	output = "Here it is: \n"
	for line in outputLines:
		output += "`"+line+"` \n"
	if 'thread_ts' in message.body:
		pass
	else:
		message.reply(output)

@respond_to('send message to (.*)', re.IGNORECASE)
def send_sms(message, number):
	attachments = [
	{
		'author_name': 'Ok. Ready to send a text to:',
		'title': '%(number)s' % {'number': re.sub(r"\s+", "", number)},
		'text': 'What\'s your message?',
		'color': '#59afe1'
        }]
	if 'thread_ts' in message.body:
		pass
	else:
		message.send_webapi('', json.dumps(attachments))

@respond_to('call (.*)', re.IGNORECASE)
def makeCall(message, number):
	if 'thread_ts' in message.body:
		chan 		= message.body['channel']
		tstamp		= message.body['thread_ts']
		thread		= message._client.webapi.im.replies(chan,tstamp)
		incoming	= thread.body['messages'][0]
		callerId	= incoming['attachments'][0]['title']
		
		if number == 'back':
			line	= incoming['attachments'][0]['footer']
			reply	= placeCall(callerId, line)
			message.reply(reply, in_thread=True)
		else:
			pass
	else:
		if number == 'back':
			chan 				= message.body['channel']
			tstamp				= message.body['ts']
			notification		= message._client.webapi.im.history(chan,tstamp, 19)
			incoming			= findLastCall(notification.body['messages'])
			callerId			= incoming['title']
			line				= incoming['footer']
			output = 'Calling back %(number)s using the %(line)s.' % {'number' : callerId, 'line' : line}
			message.reply(output)				
			output = placeCall(callerId, line)
			message.reply(output)				
		else:
			attachments = [
			{
				'author_name': 'Sure thing. Ready to call:',
				'title': '%(number)s' % {'number': re.sub(r"\s+", "", number)},
				'text': 'Using the landline or the gsm?',
				'color': '#59afe1'
	        	}]
			message.send_webapi('', json.dumps(attachments))

@respond_to('(.*)', re.IGNORECASE)
def reply_to(message, text):
	if 'thread_ts' in message.body:
		chan 		= message.body['channel']
		tstamp		= message.body['thread_ts']
		thread		= message._client.webapi.im.replies(chan,tstamp)
		incoming	= thread.body['messages'][0]
		number		= incoming['attachments'][0]['title']
		
		if (text == 'landline' or text == 'gsm'):
			reply	= placeCall(number, text)
			message.reply(reply, in_thread=True)
		elif text == 'call back':
			line	= incoming['attachments'][0]['footer']
			reply	= placeCall(number, line)
			message.reply(reply, in_thread=True)
		else:
			if number != '':
				reply = "Got that. Trying to send it out."
				message.reply(reply, in_thread=True)
				rawOutput = runProcess(["asterisk", "-rx", "dongle sms dongle0 %(number)s %(message)s" % {'number': number, 'message': text}])
				outputLines = rawOutput.splitlines()
				output = ""
				for line in outputLines:
					output += "`"+line+"` \n"
				message.reply(output, in_thread=True)
			else:
				reply = "Sorry, it seems that I lost track of the recipient."
				message.reply(reply, in_thread=True)
	else:
		if (text == 'landline' or text == 'gsm'):
			chan 				= message.body['channel']
			tstamp				= message.body['ts']
			notification		= message._client.webapi.im.history(chan,tstamp, 2)
			incoming			= notification.body['messages'][0]
			number				= incoming['attachments'][0]['title']
			reply	= placeCall(number, text)
			message.reply(reply)
		else:
			pass

