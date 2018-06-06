#coding: UTF-8
import re, json, subprocess, gammu
from slackbot.bot import respond_to

def runProcess(exe):    
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    return p.stdout.read()

@respond_to('help', re.IGNORECASE)
def help(message):
	help_message=" :wave: :robot_face: Hello! I'm @jarvis, a slackbot for talking with your personal Asterisk server easily. Here's how I work: \n\n"+\
            "  _Basic Commands:_  \n" +\
            "  `@<SLACK_BOT> call <number>` -- asks you what line to use to place the call. Answer in a thread to get connected.  \n" +\
            "  `@<SLACK_BOT> send message to <number>` -- asks what message to send to the specified phone number. Answer in a thread.  \n" +\
            "  _Advanced Commands:_  \n" +\
            "  `@<SLACK_BOT> get gsm status` -- asks about the status of the GSM line and returns the output.  \n" +\
            "  `@<SLACK_BOT> ask <request>` -- executes a request to Asterisk CLI and returns the output.  \n\n" +\
            "  Give me a try! :simple_smile: \n"
	if 'thread_ts' in message.body:
		message.reply(help_message, in_thread=False)
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
		message.reply(output, in_thread=True)
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
		message.reply(output, in_thread=True)
	else:
		message.reply(output)

@respond_to('send message to (.*)', re.IGNORECASE)
def send_sms(message, number):
	attachments = [
	{
		'author_name': '%(number)s' % {'number': number},
		'text': 'Ok. What\'s your message?',
		'color': '#59afe1'
        }]
	message.send_webapi('', json.dumps(attachments))

@respond_to('(.*)')
def reply_sms(message, text):
	if 'thread_ts' in message.body:
		chan 		= message.body['channel']
		tstamp		= message.thread_ts
		thread		= message._client.webapi.im.replies(chan,tstamp)
		incomingSMS	= thread.body['messages'][0]
		number		= incomingSMS['attachments'][0]['author_name']

		if text == 'landline':
			if number != '':
				output = runProcess(["asterisk", "-rx", "channel originate sip/999 extension %(number)s@outbound-allroutes" % {'number': number}])
				output = "I'm trying to connect you."
				message.reply(output, in_thread=True)
			else:
				reply = "Sorry, it seems that I lost track of the recipient."
				message.reply(reply, in_thread=True)
		elif text == 'gsm':
			if number != '':
				output = runProcess(["asterisk", "-rx", "channel originate sip/999 extension %(number)s@outbound-gsm" % {'number': number}])
				output = "I'm trying to connect you."
				message.reply(output, in_thread=True)
			else:
				reply = "Sorry, it seems that I lost track of the recipient."
				message.reply(reply, in_thread=True)
		else:
			if number != '':
				state_machine = gammu.StateMachine()
				state_machine.ReadConfig()
				state_machine.Init()
				sms = {
					'Text': text.decode('utf-8'),
					'SMSC': {'Location': 1},
					'Number': number,
					}
				state_machine.SendSMS(sms)
				reply = "Sent!"
				message.reply(reply, in_thread=True)
			else:
				reply = "Sorry, it seems that I lost track of the recipient."
				message.reply(reply, in_thread=True)

@respond_to('call (.*)', re.IGNORECASE)
def makeCall(message, number):
	attachments = [
	{
		'author_name': '%(number)s' % {'number': number},
		'text': 'Sure thing. Using the landline or the gsm?',
		'color': '#59afe1'
        }]
	message.send_webapi('', json.dumps(attachments))
