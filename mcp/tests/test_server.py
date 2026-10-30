"""Talk to the server in-process through a real MCP client."""

import asyncio
import json
import unittest

from mcp import Client

from nutq_mcp.server import server


def call(name, arguments):
    async def run():
        async with Client(server) as client:
            return await client.call_tool(name, arguments)
    return asyncio.run(run())


def text_of(result):
    return result.content[0].text


class ServerTest(unittest.TestCase):
    def test_lists_tools(self):
        async def run():
            async with Client(server) as client:
                return await client.list_tools()
        tools = {tool.name: tool for tool in asyncio.run(run()).tools}
        self.assertEqual(
            set(tools),
            {"convert_script", "normalize_text", "number_to_words", "clean_text", "list_languages"},
        )
        self.assertTrue(tools["convert_script"].annotations.read_only_hint)

    def test_convert(self):
        result = call("convert_script", {"text": "Забони тоҷикӣ", "lang": "tg", "to": "Arab"})
        self.assertFalse(result.is_error)
        self.assertEqual(text_of(result), "زبان تاجیکی")

    def test_normalize(self):
        result = call("normalize_text", {"text": "Нархи 25 $ аст", "lang": "tg"})
        self.assertEqual(text_of(result), "Нархи бисту панҷ доллар аст")

    def test_number(self):
        result = call("number_to_words", {"number": 4, "lang": "uz", "ordinal": True, "script": "Cyrl"})
        self.assertEqual(text_of(result), "тўртинчи")

    def test_clean(self):
        self.assertEqual(text_of(call("clean_text", {"text": "o'zbek", "lang": "uz"})), "oʻzbek")

    def test_languages(self):
        result = call("list_languages", {})
        codes = [item["code"] for item in json.loads(text_of(result))] if len(result.content) == 1 \
            else [json.loads(c.text)["code"] for c in result.content]
        self.assertEqual(codes, ["fa", "fa-AF", "tg", "uz"])

    def test_errors_are_reported(self):
        result = call("convert_script", {"text": "салом", "lang": "xx", "to": "Latn"})
        self.assertTrue(result.is_error)
        self.assertIn("unknown language", text_of(result))


if __name__ == "__main__":
    unittest.main()
