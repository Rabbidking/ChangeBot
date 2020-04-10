import svn.remote
import pytz
import tweepy
from datetime import date
from discord_webhook import DiscordWebhook, DiscordEmbed
from pbwrap import Pastebin

# Set script up to work with Twitter
auth = tweepy.OAuthHandler("YOUR_API_KEY", "YOUR_API_SECRET_KEY")
auth.set_access_token("YOUR_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN_SECRET")

#Create API object
api = tweepy.API(auth)

#PasteBin setup
API_DEV_KEY = 'YOUR_PASTEBIN_API_DEV_KEY'
pb = Pastebin(API_DEV_KEY)
pb.authenticate("PASTEBIN_USERNAME", "PASTEBIN_PASSWORD")

# Get today's date
local_tz = pytz.timezone('YOUR/TIMEZONE/HERE')
today = date.today()

def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)
	
def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%m/%d/%Y, %I:%M:%S %p')
	
discord_url = 'YOUR_WEBHOOK_URL'

#Set the URLs for the svn and the Discord webhook
r = svn.remote.RemoteClient('YOUR_SVN_ADDRESS')	#only records changes in trunk
webhook = DiscordWebhook(url=discord_url, username='SVN Changelog')

commitMadeToday = False

outfile = open("changelog.txt", "r+")
outfile.write("Today's changes:" + "\n")
outfile.write("====================\n")

webhook.avatar_url = 'https://i.imgur.com/Pi5ICIR.jpg'

def discord(u):
	global commitMadeToday
	i = 0
	
	for e in r.log_default():
				
			#creates embed
			embed = DiscordEmbed(title="Today's Updates", url=u, color=242424)
			
			if e.date.date() == today:
				if e:
					# If a change has been made today, set this variable to True
					commitMadeToday = True
				
				webhook.add_embed(embed)	#adds embed to the webhook
					
	if commitMadeToday == False:
		webhook.content = "No changes today."
		
	#execute the webhook
	webhook.execute()
				
def changelog():			
	for e in r.log_default():	
		if e.date.date() == today:
			if e:
				# If a change has been made today, set this variable to True
				commitMadeToday = True
				
			if commitMadeToday == False:
				# If no changes were made today, say so in the changelog.
				outfile.write("No changes today.\n")
				break
			
			else:
				# Write to changelog.txt
				outfile.write("Author: " + e.author + '\n')
				outfile.write("Date: " + aslocaltimestr(e.date) + '\n')
				outfile.write("Revision #" + str(e.revision) + '\n')
				outfile.write(str(e.msg) + '\n')
				outfile.write('\n')
					
		if e.date.date() != today:
			#delete all previous day's info from changelog
			outfile.truncate()
			
	#cut out extra newline at EOF
	outfile.truncate(outfile.tell() - 2)
	#close the file
	outfile.close()

# Send stuff to Pastebin, Discord, and Twitter
changelog()
url = pb.create_paste_from_file('./changelog.txt', 0, str(today.strftime("%m/%d/%Y")) + " Changelog", "N")
discord(url)
api.update_status(str(today.strftime("%m/%d/%Y")) + " changelog: " + url, tweet_mode = "extended")
