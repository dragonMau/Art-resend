from discord_webhook import DiscordWebhook
import requests
from time import time, asctime
import discord
import json
import config

start_time = time()
def log(*text, sep=" ", end="\n"):
    sec = (time()-start_time)%3600
    print(
    f"({int(sec//60):02d}:{int(sec%60):02d}) "\
    +sep.join(map(str, text))+str(end), sep="", end="")

class Sender:
    def random(self):
        link = requests.get("https://api.waifu.pics/sfw/neko")
        return json.loads(link.content)["url"]
        
    def send_art(self, art="", file=False, cont=""):
        if art == "": art = self.random()
        log("creating webhook...")
        webhook = DiscordWebhook(
        url=self.urls,
        username=self.data["username"],
        avatar_url=self.data["avatar_url"],
        content=cont)
        log("webhook created, creating art...")
        if not file:
            log("    downloading from url...")
            art = requests.get(art).content
        if file:
            log("    opening from file...")
            art = art.fp.read()
            
        log("art created, adding file...")
            
        webhook.add_file(file = art,
        filename=f"{asctime()}.png")
        
        log("file added, executing webhook...")
        response = webhook.execute()
        log(f"webhook executed, {response}")

    def __init__(self):
        self.urls = config.urls
        self.data = config.data
        self.bank = config.bank
        self.token = config.token
           
 
 
sender = Sender()     

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
        log("setting up profile...")
        log("looking for", sender.data["id"])
        try:
            dnmau = await client.fetch_user(
                      sender.data["id"])
            log(f"found user {dnmau}, ...")
            sender.data["username"] = dnmau.name
            sender.data["avarar_url"] = dnmau.avatar
            log("configured: ",
                   "\n          ", sender.data["username"],
                   "\n          ", sender.data["avatar_url"])
        except discord.NotFound:
            log("user not found, using defaults")
        
        log("started, getting bank channel...")
        ch = client.get_channel(sender.bank)
        log("got bank channel.")
        num = int(input("how many arts to send?: "))
        times = 0
        log(f"sending {num} arts...")
        
        history = ch.history(oldest_first=True,
                                           limit=num)
        async for first in history:
            log("got message")
            if first.attachments:
                first_art = await first.attachments[-1].to_file()
                log("got image, sending...")
                sender.send_art(first_art, file=True)
            else:
                log("not found image, sending random...")
                sender.send_art(cont="empty message, random image")
            times+=1
            log("sent, deleting...")
            await first.delete()
            log(f"done {num} arts")
        
        if times < num:
            log("bank is empty, filling with randoms...")
        while times < num:
            sender.send_art(cont="bank is empty, random image")
            times+=1
            log(f"done {times}/{num} arts")
        
        log("finished!")
        await client.close()

if __name__=="__main__":
    log("starting...")
    client.run(sender.token)
