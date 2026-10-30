import io
import unittest
from contextlib import redirect_stdout

import nutq
from nutq.__main__ import main
from nutq.scripts import canonical_script


class RegistryTest(unittest.TestCase):
    def test_builtin_languages(self):
        codes = [l.code for l in nutq.languages() if not l.code.startswith("x-")]
        self.assertEqual(codes, ["fa", "fa-AF", "tg", "uz"])

    def test_aliases(self):
        self.assertEqual(nutq.get_language("prs").code, "fa-AF")
        self.assertEqual(nutq.get_language("FA_af").code, "fa-AF")
        self.assertEqual(nutq.get_language("tgk").code, "tg")
        self.assertEqual(nutq.get_language("uz-Cyrl").code, "uz")

    def test_unknown_language(self):
        with self.assertRaises(nutq.UnsupportedError):
            nutq.get_language("xx")

    def test_unknown_script_for_language(self):
        with self.assertRaises(nutq.UnsupportedError):
            nutq.convert("салом", "uz", to="Arab")

    def test_register_custom_language(self):
        upper = nutq.Language(
            code="x-test", name="Test", native_name="test",
            default_script="Latn", scripts=("Latn",),
            cardinal=str, ordinal=lambda n: f"{n}th",
            normalize=str.upper, clean=str.strip,
        )
        nutq.register(upper)
        self.assertEqual(nutq.normalize("abc", "x-test"), "ABC")
        self.assertEqual(nutq.number_to_words(4, "x-test", ordinal=True), "4th")


class ScriptsTest(unittest.TestCase):
    def test_detect(self):
        self.assertEqual(nutq.detect_script("Салом, dunyo!"), "Cyrl")
        self.assertEqual(nutq.detect_script("سلام dunyo"), "Latn")
        self.assertEqual(nutq.detect_script("سلام دنیا"), "Arab")
        self.assertEqual(nutq.detect_script("Oʻzbek"), "Latn")
        self.assertIsNone(nutq.detect_script("123 !"))

    def test_canonical_names(self):
        self.assertEqual(canonical_script("latin"), "Latn")
        self.assertEqual(canonical_script("ARAB"), "Arab")
        with self.assertRaises(ValueError):
            canonical_script("klingon")

    def test_same_script_is_unchanged(self):
        self.assertEqual(nutq.convert("Душанбе", "tg", to="Cyrl"), "Душанбе")


class CliTest(unittest.TestCase):
    def run_cli(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            main(list(args))
        return out.getvalue().strip()

    def test_commands(self):
        self.assertEqual(self.run_cli("convert", "-l", "tg", "--to", "Latn", "Душанбе"), "Dushanbe")
        self.assertEqual(self.run_cli("convert", "-l", "uz", "-t", "cyrillic", "Toshkent"), "Тошкент")
        self.assertEqual(self.run_cli("number", "-l", "tg", "2026"), "ду ҳазору бисту шаш")
        self.assertEqual(self.run_cli("number", "-l", "uz", "--ordinal", "2"), "ikkinchi")
        self.assertEqual(self.run_cli("normalize", "-l", "fa", "۱۵٪"), "پانزده درصد")
        self.assertEqual(self.run_cli("clean", "-l", "tg", "Тoҷик"), "Тоҷик")
        self.assertIn("Tajik", self.run_cli("languages"))


if __name__ == "__main__":
    unittest.main()
