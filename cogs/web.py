from config.config import access, status, delete_after_time
from utils.date import days, months
from utils import tools
from utils import html_parser


from discord.ext import commands, tasks
from translate import Translator
from bs4 import BeautifulSoup
import requests
import datetime
import discord
import random
import aiohttp
import json
import re


class Web(commands.Cog):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        # self.to_language = "fr"
        # self.from_language = "en"
        # self.translator = Translator(to_lang=to_language, from_lang=from_language)

    @commands.command(name="traduit", aliases=['t', 'trad'])
    async def translate(self,ctx, languages:str, *, message:str):
        """Traduit un message."""

        try:
            if '/'in languages:
                from_lang, to_lang = languages.split('/')
                if len(to_lang)!=2 or len(from_lang)!=2:
                    raise Exception("Ce n'est pas un langage du code ISO.")
                translator = Translator(to_lang=to_lang, from_lang=from_lang)
            else:
                to_lang = languages
                if len(to_lang)!=2:
                    raise Exception("Ce n'est pas un langage du code ISO.")
                translator = Translator(to_lang=to_lang)
            translation = translator.translate(message)
            await ctx.send(translation)
        except Exception as e:
            msg = str(e)
            msg += "\nVous devez tapez: '.traduit [langue iso] [message]'. Il y a 2 options:"
            msg += "\n1) .traduit `fr` without the origin language => sans le langage d'origine."
            msg += "\n2) .traduit `en/fr` with the origin language => avec le langage d'origine."
            msg += "\n\nRegarder ce lien pour connaître le code iso en 2 lettres d'une langue."
            msg += "\nhttps://en.wikipedia.org/wiki/ISO_639-1"
            await ctx.send(msg)

    @commands.command()
    async def bitcoin(self, ctx:commands.Context):
        """Donne la valeur du bitcoin en dollar."""
        url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
        async with aiohttp.ClientSession() as session:  # Async HTTP request
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            await ctx.send("Le prix du bitcoin est: $" + response['bpi']['USD']['rate'])

    @commands.command()
    async def meme(self, ctx):
        """Envoie un meme."""
        response = requests.get("https://meme-api.herokuapp.com/gimme").json()
        await ctx.send(response['title']+'\n'+response['url'])

    @commands.command(name="insulte")
    async def insult(self, ctx, name=""):
        """Insulte une personne."""
        url = "http://strategicalblog.com/liste-dinsultes-francaises-pas-trop-vulgaires/"
        await ctx.send(random.choice(re.findall("\n•\t(.*)<br />", requests.get(url).text))+" "+name)

    @commands.command(name="wikipedia", aliases=["wiki"])
    async def wikipedia(self, ctx, *search_list, n=500, d=5):
        """Fais une recherche sur wikipédia."""
        languages = ["fr", "en"]
        for language in languages:
            if search_list[-1][:1] == "/":
                n = int(search_list[-1][1:])
                search_list = search_list[:-1]
            search_list = [search[0].upper()+search[1:] for search in search_list]
            search = "_".join(search_list)
            resp = requests.get(f"https://{language}.wikipedia.org/wiki/{search}")
            parser = html_parser.Parser('div', 'class', 'mw-parser-output', fetched_tags=["p", "li", "a"])
            parser.load(resp.text)
            lines = parser.result.split('\n')
            deleting = ["wiki", "wikti", "ne cite pas suffisamment ses sources", "quelles sources sont attendues ?", "testez votre navigateur"]
            new_lines = []
            for line in lines:
                found = False
                for s in deleting:
                    if s in line.lower():
                        found = True
                        break;
                if not found and line.strip()!="":
                    new_lines.append(line)
            parser.result = "\n".join(new_lines)
            if len(parser.result):
                await ctx.send(parser.result[:n]+"...")
                return
        await ctx.send(f"La page {search} n'existe pas sur Wikipedia.")
        # session = requests.Session()
        # url = "https://fr.wikipedia.org/w/api.php"
        # search = " ".join(search)
        # params = {"action":"query", "format":"json", "list":"search", "srsearch":search}
        # response = session.get(url=url, params=params)
        # data = response.json()
        # cmd = f"Les pages similaires sont:"
        # print(data['query']['search'])
        # cmd += "\n".join([e['title'] for e in data['query']['search'][:d]])
        # await ctx.send(cmd)

    @commands.command(name="uncyclopédie", aliases=["fwiki", "désencyclopédie"])
    async def uncyclopedia(self, ctx, search):
        """Fais une recherche sur désencyclopédie."""
        async with self.bot.channel.typing():
            url = "https://desencyclopedie.org/wiki/"
            html = BeautifulSoup(requests.get(url+search).text, 'html.parser')
            response = ""
            i = 0
            inp = ""
            while len(response)+len(inp)<1000:
                response += inp
                inp += html.body.find(class_='mw-parser-output').find_all('p')[i].text
                i+=1
            await ctx.send(response)



def setup(bot):
    bot.add_cog(Web(bot))