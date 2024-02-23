import socket
import requests
import datetime
import threading
import time
from collections import namedtuple
import json
import StreamerGame
from datetime import datetime, timedelta

OAUTH_TOKEN = "oauth:YOUR_TWITCH_API_KEY"
riotapikey = "YOUR_RIOT_API_KEY"
TEMPLATE_COMMANDS = {
    '!rank': "@{message.user} {message.mesag}"
}
Message = namedtuple(
    "Message",
    "prefix user channel irc_command irc_args text text_command text_args mesag"
)


class Bot:
    def __init__(self):
        self.irc_server = "irc.twitch.tv"
        self.irc_port = 6667
        self.oauth_token = OAUTH_TOKEN
        self.username = "HayalBot"
        self.channels = []
        # with open("Channels.json", "r") as channels:
        #    jchannels = json.load(channels)
        # for i in jchannels:
        #    self.channels.append(i)
        self.custom_command = {
            '!date': self.replay_with_date,
            '!ping': self.replay_to_ping,
        }

    def json_degisiklikleri_izle(self):
        self.onceki_veri = []

        time.sleep(2)
        while True:
            with open("Channels.json", 'r') as dosya:
                yeni_veri = json.load(dosya)
            if yeni_veri != self.onceki_veri:
                degisiklikler = self.farklari_bul(self.onceki_veri, yeni_veri)
                self.ozel_islem(degisiklikler)
                self.onceki_veri = yeni_veri
            time.sleep(1)  # Dosya kontrol sıklığını ayarlayabilirsiniz*

    def farklari_bul(self, eski_veri, yeni_veri):
        degisiklikler = {}

        for anahtar in yeni_veri:
            if anahtar not in eski_veri or yeni_veri[anahtar] != eski_veri[anahtar]:
                degisiklikler[anahtar] = yeni_veri[anahtar]

        return degisiklikler

    def ozel_islem(self, degisiklikler):
        for anahtar, deger in degisiklikler.items():
            self.send_command(f'JOIN #{anahtar}')
            self.channels.append(anahtar)

    def send_privmsg(self, channel, text):
        self.send_command(f'PRIVMSG #{channel} :{text}')

    def send_command(self, command):
        if 'PASS' not in command:

            if "mesag=None" not in str(command):
                print(f'{datetime.utcnow() + timedelta(hours=3)}: < {command}')
        self.irc.send((command + '\r\n').encode())

    def connect(self):
        self.irc = socket.socket()
        self.irc.connect((self.irc_server, self.irc_port))
        self.send_command(f'PASS {self.oauth_token}')
        self.send_command(f'NICK {self.username}')
        for channel in self.channels:
            self.send_command(f'JOIN #{channel}')
        self.loop_for_messages()

    def get_user_from_prefix(self, prefix):
        domain = prefix.split('!')[0]
        if domain.endswith('.tmi.twitch.tv'):
            return domain.replace('.tmi.twitch.tv', '')
        if '.tmi.twitch.tv' not in domain:
            return domain
        return None

    def parse_message(self, received_msg):
        parts = received_msg.split(' ')
        prefix = None
        user = None
        channel = None
        mesag = None
        text = None
        text_command = None
        text_args = None
        irc_command = None
        irc_args = None

        if parts[0].startswith(':'):
            prefix = parts[0][1:]
            user = self.get_user_from_prefix(prefix)
            parts = parts[1:]

        text_start = next(
            (idx for idx, part in enumerate(parts) if part.startswith(':')),
            None
        )
        if text_start is not None:
            text_parts = parts[text_start:]
            text_parts[0] = text_parts[0][1:]
            text = ' '.join(text_parts)
            text_command = text_parts
            text_args = text_parts[1:]
            parts = parts[:text_start]

        irc_command = parts[0]
        irc_args = parts[1:]
        hash_start = next(
            (idx for idx, part in enumerate(irc_args) if part.startswith('#')),
            None
        )
        if hash_start is not None:
            channel = irc_args[hash_start][1:]

        if text != None:
            with open("Channels.json", "r") as channeld:
                jchannels = json.load(channeld)
            if "!rank" in text:
                gameid = StreamerGame.StreamerGame(channel)
                if gameid == "516575":
                    if jchannels[channel]['Valorant'] != None:
                        try:
                            link = f"https://api.kyroskoh.xyz/valorant/v1/mmr/{jchannels[channel]['Valorant']['region']}/{jchannels[channel]['Valorant']['valonick']}/{jchannels[channel]['Valorant']['valotag']}?display=0"
                            r = requests.get(link)
                            mesag = f"{r.text}"
                            if "radiant" in mesag.lower() or "immortal" in mesag.lower():
                                link = f"https://api.kyroskoh.xyz/valorant/v1/leaderboard/{jchannels[channel]['Valorant']['region']}/{jchannels[channel]['Valorant']['valonick']}/{jchannels[channel]['Valorant']['valotag']}?display=0"
                                r = requests.get(link)
                                if r.text != "Request failed with status code 404.":
                                    mesag = f"{jchannels[channel]['Valorant']['valonick']}#{jchannels[channel]['Valorant']['valotag']}, {mesag}  sıralama: {r.text.split('#')[1].split(' ')[0]}"
                        except Exception as e:

                            print(f"{datetime.utcnow() + timedelta(hours=3)}: ", e)
                            mesag = "Sorry, we encountered an issue."
                    else:
                        mesag = "No registered Valorant account found!"
                    mesag = mesag
                elif gameid == "21779":
                    if jchannels[channel]['LOL'] != None:
                        try:
                            link = f"https://{jchannels[channel]['LOL']['region']}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{jchannels[channel]['LOL']['riotid']}?api_key={riotapikey}"
                            r = requests.get(link)
                            puuid = f"{r.json()['id']}"
                            mesag = ""
                        except:
                            mesag = "Sorry, we encountered an issue."
                        if mesag != "Sorry, we encountered an issue.":
                            linkpuuid = f"https://{jchannels[channel]['LOL']['region']}.api.riotgames.com/lol/league/v4/entries/by-summoner/{puuid}?api_key={riotapikey}"
                            r2 = requests.get(linkpuuid)
                            if (r2.json() != []):
                                mesag = f"{r2.json()[0]['tier']}-{r2.json()[0]['rank']}"
                            else:
                                mesag = "Don't have rank"
                    else:
                        mesag = "No registered League of Legends account found!"
                else:
                    mesag = f"This is game not have a rank system!"

        message = Message(
            prefix=prefix,
            user=user,
            channel=channel,
            irc_command=irc_command,
            irc_args=irc_args,
            text=text,
            text_command=text_command,
            text_args=text_args,
            mesag=mesag
        )

        return message

    def handle_template_command(self, message, text_command, template):
        text = template.format(**{'message': message})
        self.send_privmsg(message.channel, text)

    def replay_with_date(self, message):
        formatted_date = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        text = f'Here you go {message.user}, the date is: {formatted_date}.'
        self.send_privmsg(message.channel, text)

    def replay_to_ping(self, message):
        text = f'Hey {message.user}, Nice Ping!'
        self.send_privmsg(message.channel, text)

    def handle_message(self, received_msg):
        if len(received_msg) == 0:
            return
        message = self.parse_message(received_msg)
        if "mesag=None" not in str(message):
            print(f'{datetime.utcnow() + timedelta(hours=3)}: > {message}')

        if message.irc_command == 'PING':
            self.send_command('PONG :tmi.twitch.tv')
        if message.irc_command == 'PRIVMSG':
            if message.text_command[0] in TEMPLATE_COMMANDS:
                self.handle_template_command(
                    message,
                    message.text_command,
                    TEMPLATE_COMMANDS[message.text_command[0]],
                )
            if message.text_command[0] in self.custom_command:
                self.custom_command[message.text_command[0]](message)

    def loop_for_messages(self):
        while True:
            received_msgs = self.irc.recv(2048).decode()

            for received_msg in received_msgs.split('\r\n'):
                self.handle_message(received_msg)


bot = Bot()


def main():
    while True:
        try:
            bot.connect()
        except Exception as e:
            if "mesag=None" not in e:
                print(f"{datetime.utcnow() + timedelta(hours=3)}: ERROR:", e)


def mainStart():
    while True:
        mainf = main()
        print("deneme3")
        mainTh = threading.Thread(target=mainf)
        mainTh.start()


threading.Thread(target=mainStart).start()
threading.Thread(target=bot.json_degisiklikleri_izle()).start()