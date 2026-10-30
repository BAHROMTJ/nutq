"""Launch the installed ``nutq-mcp`` command and talk to it over stdio."""

import asyncio
import shutil
import unittest

from mcp import Client, StdioServerParameters


@unittest.skipUnless(shutil.which("nutq-mcp"), "nutq-mcp is not installed")
class StdioTest(unittest.TestCase):
    def test_round_trip(self):
        async def run():
            params = StdioServerParameters(command=shutil.which("nutq-mcp"))
            async with Client(params) as client:
                return await client.call_tool(
                    "normalize_text", {"text": "۱۴۰۵/۰۱/۱۲", "lang": "fa"}
                )
        result = asyncio.run(run())
        self.assertEqual(result.content[0].text, "دوازدهم فروردین هزار و چهارصد و پنج")


if __name__ == "__main__":
    unittest.main()
