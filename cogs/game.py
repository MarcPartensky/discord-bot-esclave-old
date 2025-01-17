from config.config import access, status, delete_after_time, masters
from config import emoji
from utils import tools

from discord.ext import commands, tasks
import discord
import random
import time


class Game(commands.Cog):
    def __init__(self, bot, **kwargs):
        super().__init__(**kwargs)
        self.bot = bot
        self.max_coins = 5

    @property
    def bank(self):
        return self.bot.get_cog("Bank")

    @commands.command()
    async def pierre(self, ctx, coins=2, player:discord.User=None):
        """Joue pierre au pierre feuille ciseaux."""
        await self.pfc(ctx, "pierre", coins, player)

    @commands.command(aliases=["papier"])
    async def feuille(self, ctx, coins=2, player:discord.User=None):
        """Joue feuille au pierre feuille ciseaux."""
        await self.pfc(ctx, "feuille", coins, player)

    @commands.command()
    async def ciseaux(self, ctx, coins=2, player:discord.User=None):
        """Joue ciseaux au pierre feuille ciseaux."""
        await self.pfc(ctx, "ciseaux", coins, player)

    @commands.command(aliases=["pierre_feuille_ciseaux"])
    async def pfc(self, ctx, user_choice, coins=2, player:discord.User=None):
        "Joue au pierre feuille ciseaux."
        player = player or ctx.author
        if ctx.author!=player and not ctx.author.id in masters:
            await ctx.send("Vous n'êtes pas autorisé à jouer à la place de cette personne.")
            return
        l = {"pierre":0, "feuille":1, "ciseaux":2}
        self.bank.select(table="money", column="money", conditions={"customer":player.id})
        result = self.bank.fetchone()
        if not user_choice in l:
            await ctx.send("Vous devez choisir entre pierre, feuille ou ciseaux.")
        elif coins>self.max_coins:
            await ctx.send(f"Vous ne pouvez pas miser au delà de {self.max_coins} {emoji.coin}.")
        elif not result:
            if player==ctx.author:
                await ctx.send(f"Vous n'avez pas de compte bancaire.")
            else:
                await ctx.send(f"{player.name} n'a pas compte bancaire.")
            await ctx.send("Pour créer un compte tapez: '{self.bot.get_prefix()}ouvrir_un_compte'.")
        elif result[0]-coins<0:
            await ctx.send(f"Vous n'avez pas assez d'argent pour miser une telle somme.")
        else:
            bot_choice = random.choice(list(l.keys()))
            await ctx.send(bot_choice)
            if (l[user_choice]+1)%3==l[bot_choice]:
                self.bank.loose(player, coins)
                if ctx.author==player:
                    msg = f"Vous avez perdu {coins} {emoji.coin}."
                else:
                    msg = f"{player.name} a perdu {coins} {emoji.coin}."
                await ctx.send(msg)
            elif (l[bot_choice]+1)%3==l[user_choice]:
                self.bank.win(player, coins)
                if ctx.author==player:
                    msg = f"Vous avez gagné {coins} {emoji.coin}."
                else:
                    msg = f"{player.name} a gagné {coins} {emoji.coin}."
                await ctx.send(msg)
            else:
                await ctx.send("Match nul.")

    @commands.command()
    async def pile(self, ctx, coins=2, player:discord.User=None):
        """Joue pile au pile ou face."""
        await self.pf(ctx, "pile", coins, player)

    @commands.command()
    async def face(self, ctx, coins=2, player:discord.User=None):
        """Joue face au pile ou face."""
        await self.pf(ctx, "face", coins, player)

    @commands.command(aliases=["pile_ou_face"])
    async def pf(self, ctx, user_choice, coins=2, player:discord.user=None):
        "Joue au pile ou face."
        player = player or ctx.author
        if ctx.author!=player and not ctx.author.id in masters:
            await ctx.send("Vous n'êtes pas autorisé à jouer à la place de cette personne.")
            return
        l = ["pile", "face"]
        self.bank.select(table="money", column="money", conditions={"customer":player.id})
        result = self.bank.fetchone()
        if not user_choice in l:
            await ctx.send("Vous devez choisir entre pile ou face.")
        elif coins>self.max_coins:
            await ctx.send(f"Vous ne pouvez pas miser au delà de {self.max_coins} {emoji.coin}")
        elif not result:
            if player==ctx.author:
                await ctx.send(f"Vous n'avez pas de compte bancaire.")
            else:
                await ctx.send(f"{player.name} n'a pas compte bancaire.")
            await ctx.send("Pour créer un compte tapez: '{self.bot.get_prefix()}ouvrir_un_compte'.")
        elif result[0]-coins<0:
            await ctx.send(f"Vous n'avez pas assez d'argent pour miser une telle somme.")
        else:
            bot_choice = random.choice(l)
            await ctx.send(bot_choice)
            if user_choice==bot_choice:
                self.bank.win(player, coins)
                if ctx.author==player:
                    msg = f"Vous avez gagné {coins} {emoji.coin}."
                else:
                    msg = f"{player.name} a gagné {coins} {emoji.coin}."
                await ctx.send(msg)
            else:
                self.bank.loose(player, coins)
                if ctx.author==player:
                    msg = f"Vous avez perdu {coins} {emoji.coin}."
                else:
                    msg = f"{player.name} a perdu {coins} {emoji.coin}."
                await ctx.send(msg)


def setup(bot):
    bot.add_cog(Game(bot))