from __future__ import annotations

__all__ = ['Generator']

import aiofiles

from aiohttp import ClientSession
from typing import Optional
from os import getcwd

BASE_URL = "http://apimeme.com/meme"

class Generator:
	def __init__(self) -> None:
		self.session: Optional[ClientSession] = None

	async def __aenter__(self) -> "Generator":
		self.session = ClientSession()
		return self

	async def close_session(self) -> None:
		if self.session is not None:
			await self.session.close()

	async def __aexit__(self, *args) -> None:
		await self.close_session()


	async def create(self, 
		meme: str, 
		top_text: str = "Top Text", 
		bottom_text: str = "Bottom Text",
		save_location: str = None,
		file_name: str = "meme",
		file_extension: str = "jpeg"
	) -> int:
		if self.session is None:
			self.session = ClientSession()

		params = {
			'meme': meme,
			'top': top_text,
			'bottom': bottom_text
		}

		async with self.session.get(BASE_URL, params=params) as response:
			if response.status == 200:
				async with aiofiles.open(f"{save_location or getcwd()}/{file_name}.{file_extension}", mode='wb+') as f:
					await f.write(await response.read())

			return response.status