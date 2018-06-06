# Slackbot for Asterisk

A plugin for the <a href="https://github.com/lins05/slackbot">Slack chat bot</a> by Shuai Lin to interact with Asterisk

Open the script and replace ```<SLACK_BOT>``` with the name of your application.

## Usage

Just type help to get a list of supported commands. 

```
call <number> -- asks you what line to use to place the call. Answer in a thread to get connected.
send message to <number>` -- asks what message to send to the specified phone number. Answer in a thread.
get gsm status -- asks about the status of the GSM line and returns the output.
ask <request> -- executes a request to Asterisk CLI and returns the output.
```

Basically, to place a call, ask ```call 0123456789```. Your bot will then ask you wether it should use your SIP landline or your GSM line - with chan_dongle. Reply ```landline``` or ```gsm``` in a thread. The call will be placed - your extension will be called first; and when you pick up the phone, the call to the recipient is initiated.

To send a text message, juste type ```send message to 0123456789```. Your bot will then ask for your message. Reply to that request in a thread, just with your message to the reciepent. It will then be sent using <a href="https://wammu.eu/gammu/">Gammu</a>. The same way - in a thread -, you can reply to an incoming text message that your've been previously <a href="https://github.com/Casualtek/Asterisk-Notify-Slack">notified of</a>.

Enjoy!

License
----

MIT
