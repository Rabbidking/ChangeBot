import svn.remote
import pytz
import tweepy
from datetime import date
from discord_webhook import DiscordWebhook, DiscordEmbed
from pbwrap import Pastebin

# Set script up to work with Twitter (obtain via Twitter dev page)
auth = tweepy.OAuthHandler("YOUR API KEY", "YOUR API SECRET KEY")	#API key, API secret key
auth.set_access_token("YOUR ACCESS TOKEN", "YOUR ACCESS TOKEN SECRET")	#Access token, access token secret

#Create API object
api = tweepy.API(auth)

#PasteBin setup
API_DEV_KEY = 'YOUR PASTEBIN API DEV KEY'
pb = Pastebin(API_DEV_KEY)
pb.authenticate("YOUR PASTEBIN USERNAME", "YOUR PASTEBIN PASSWORD")

# Get today's date
local_tz = pytz.timezone('YOUR_TIMEZONE')
today = date.today()

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt) # .normalize might be unnecessary
	
def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%m/%d/%Y, %I:%M:%S %p')

#Set the URLs for the svn and the Discord webhook
r = svn.remote.RemoteClient('ADDRESS TO YOUR SVN SERVER')
webhook = DiscordWebhook(url='YOUR DISCORD WEBHOOK URL', username='SVN Changelog')

webhook.avatar_url = 'https://i.imgur.com/Pi5ICIR.jpg'

commitMadeToday = False

outfile = open("changelog.txt", "r+")
outfile.write("Today's changes:" + "\n")
outfile.write("====================\n")

for e in r.log_default():
	#check svn events
	
	#creates embed
	embed = DiscordEmbed(title="Today's Updates", color=242424)
	
	if e.date.date() == today:
		#ONLY print today's changes to the Discord and changelog.txt
		
		if e:
			# If a change has been made today, set this variable to True
			commitMadeToday = True
			
		# Set up embed information
		embed.add_embed_field(name='Author', value=str(e.author))
		embed.add_embed_field(name='Date', value=str(aslocaltimestr(e.date)))
		embed.add_embed_field(name='Revision', value=str(e.revision))
		embed.add_embed_field(name='Commit Message', value=str(e.msg))
		webhook.add_embed(embed)	#adds embed to the webhook
		
		# Write to changelog.txt
		outfile.write("Author: " + e.author + '\n')
		outfile.write("Date: " + aslocaltimestr(e.date) + '\n')
		outfile.write("Revision #" + str(e.revision) + '\n')
		outfile.write(e.msg + '\n')
		outfile.write('\n')
		
	if commitMadeToday == False:
		# If no changes were made today, say so in the changelog.
		webhook.content = "No changes today."
		outfile.write("No changes today.\n")
		break
				
	if e.date.date() != today:
		#delete all previous day's info from changelog
		outfile.truncate()
		
#cut out extra newline at EOF
outfile.truncate(outfile.tell() - 2)

# Send stuff to Pastebin and Twitter
url = pb.create_paste_from_file('./changelog.txt', 0, str(today.strftime("%m/%d/%Y")) + " Changelog", "N")
api.update_status(str(today.strftime("%m/%d/%Y")) + " changelog: " + url, tweet_mode = "extended")

#close the file
outfile.close()

#execute the webhook
webhook.execute()
