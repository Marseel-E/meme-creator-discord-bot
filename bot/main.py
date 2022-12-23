from os import environ
from traceback import print_tb

from discord import Status, Game, Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv('.env')

from utils import Default, log


class MemeCreator(Bot):
	def __init__(self) -> None:
		super().__init__(
			command_prefix=".",
			case_sensitive=False,
			status=Status.online,
			intents=Intents.default(),
			activity=Game("/create"),
			application_id=environ.get("APP_ID"),
			description="create memes n shit"
		)


	async def on_ready(self) -> None:
		log("status", "running")


	async def setup_hook(self) -> None:
		try:
			await self.tree.sync()
			await self.tree.sync(guild=Default.test_server)
		except Exception as e:
			log("error", "failed to sync commands")
			print_tb(e)
		else:
			log("status", "synced commands")

bot = MemeCreator()


from discord.app_commands import guilds, describe, autocomplete, Choice
from discord import Interaction as Inter, File

from apimeme import Generator

from os import getcwd, remove
from json import loads, dumps

from typing import List

MEMES_PATH: str = f"{getcwd()}/memes.json"


async def template_autocomplete(_inter: Inter, current: str) -> List[Choice[str]]:
	with open(MEMES_PATH, 'r') as f:
		memes = loads(f.read())

		return [Choice(name=template, value=template) for template in memes if current.lower() in template.lower()]


@bot.tree.command(description="Create a meme")
@guilds(Default.test_server)
@describe(template="The meme template", top_text="The top text", bottom_text="The bottom text")
@autocomplete(template=template_autocomplete)
async def create(inter: Inter, template: str, top_text: str = "TOP TEXT", bottom_text: str = "BOTTOM TEXT") -> None:
	IMAGE_PATH: str = f"{getcwd()}/memes"

	async with Generator() as session:
		status = await session.create(template, top_text, bottom_text, save_location=IMAGE_PATH, file_name=str(inter.user.id))

		if status != 200:
			await inter.response.send_message("Template doesn't exist. Try following the same format, seperate words with dashes `-`, and Capitalize every word.", ephemeral=True)

			return

	with open(MEMES_PATH, 'r') as f:
		memes = loads(f.read())

		if template not in memes:
			with open(MEMES_PATH, 'w') as f:
				memes.append(template)

				f.write(dumps(memes))

	await inter.response.send_message(file=File(f"{IMAGE_PATH}/{inter.user.id}.jpeg"))

	remove(f"{IMAGE_PATH}/{inter.user.id}.jpeg")


@bot.tree.command(description="Check available meme templates")
@guilds(Default.test_server)
async def templates(inter: Inter) -> None:
	await inter.response.send_message("You can see all the available meme templates here: <https://apimeme.com>\n__Make sure to follow the same format!__ Seperate words with dashes `-`, and Capitalize every word.", ephemeral=True)


if __name__ == '__main__':
	bot.run(environ.get("TOKEN"))