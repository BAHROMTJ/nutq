import unittest

import nutq


class NumbersTest(unittest.TestCase):
    def test_cardinals(self):
        cases = {
            0: "nol", 1: "bir", 11: "oʻn bir", 21: "yigirma bir", 40: "qirq",
            100: "yuz", 125: "yuz yigirma besh", 300: "uch yuz", 1000: "ming",
            1001: "ming bir", 2026: "ikki ming yigirma olti",
            1_000_000: "bir million", 3_000_015: "uch million oʻn besh",
            -5: "minus besh",
        }
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(nutq.number_to_words(number, "uz"), expected)

    def test_ordinals(self):
        cases = {1: "birinchi", 2: "ikkinchi", 3: "uchinchi", 4: "toʻrtinchi",
                 6: "oltinchi", 7: "yettinchi", 20: "yigirmanchi", 30: "oʻttizinchi",
                 100: "yuzinchi"}
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(nutq.number_to_words(number, "uz", ordinal=True), expected)

    def test_cyrillic_output(self):
        self.assertEqual(nutq.number_to_words(2026, "uz", script="Cyrl"), "икки минг йигирма олти")
        self.assertEqual(nutq.number_to_words(4, "uz", script="Cyrl", ordinal=True), "тўртинчи")


class TranslitTest(unittest.TestCase):
    def test_to_latin(self):
        cases = {
            "Ўзбекистон": "Oʻzbekiston", "Тошкент": "Toshkent", "Ғалаба": "Gʻalaba",
            "ер": "yer", "Европа": "Yevropa", "поезд": "poyezd", "объект": "obʼyekt",
            "цирк": "sirk", "концерт": "konsert", "милиция": "militsiya",
            "маъно": "maʼno", "ШАҲАР": "SHAHAR", "Шаҳар": "Shahar",
        }
        for cyrillic, latin in cases.items():
            with self.subTest(word=cyrillic):
                self.assertEqual(nutq.convert(cyrillic, "uz", to="Latn"), latin)

    def test_to_cyrillic(self):
        cases = {
            "Oʻzbekiston": "Ўзбекистон", "yoʻl": "йўл", "ekran": "экран",
            "poyezd": "поезд", "yer": "ер", "Yevropa": "Европа", "Isʼhoq": "Исҳоқ",
            "SHAHAR": "ШАҲАР", "Gʻalaba": "Ғалаба", "maʼno": "маъно",
        }
        for latin, cyrillic in cases.items():
            with self.subTest(word=latin):
                self.assertEqual(nutq.convert(latin, "uz", to="Cyrl"), cyrillic)

    def test_ascii_apostrophes(self):
        self.assertEqual(nutq.convert("O'zbekiston, g‘alaba", "uz", to="Cyrl"), "Ўзбекистон, ғалаба")

    def test_round_trip(self):
        for word in ["Ўзбекистон", "Тошкент", "Самарқанд", "ғалаба", "маъно", "поезд", "Европа"]:
            with self.subTest(word=word):
                self.assertEqual(nutq.convert(nutq.convert(word, "uz", to="Latn"), "uz", to="Cyrl"), word)


class CleanTest(unittest.TestCase):
    def test_apostrophes(self):
        self.assertEqual(nutq.clean("O'zbekiston, ma'no", "uz"), "Oʻzbekiston, maʼno")

    def test_latin_in_cyrillic(self):
        self.assertEqual(nutq.clean("Тoшкент", "uz"), "Тошкент")


class NormalizeTest(unittest.TestCase):
    def check(self, cases):
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(nutq.normalize(text, "uz"), expected)

    def test_latin(self):
        self.check({
            "Narxi 25 $": "Narxi yigirma besh dollar",
            "2026-yil 12-mart": "ikki ming yigirma oltinchi yil oʻn ikkinchi mart",
            "12.03.2026": "ikki ming yigirma oltinchi yil oʻn ikkinchi mart",
            "15% chegirma": "oʻn besh foiz chegirma",
            "2,5 kg": "ikki butun oʻndan besh kilogramm",
            "10000 so'm": "oʻn ming soʻm",
            "3-chi": "uchinchi",
            "soat 14:30": "soat oʻn toʻrt oʻttiz daqiqa",
            "AQSH": "Amerika Qoʻshma Shtatlari",
            "1991 yil 31 avgust": "ming toʻqqiz yuz toʻqson birinchi yil oʻttiz birinchi avgust",
            "+998 71 123 45 67": "toʻqqiz yuz toʻqson sakkiz, yetmish bir, yuz yigirma uch, qirq besh, oltmish yetti",
        })

    def test_cyrillic(self):
        self.check({
            "Нархи 25 $": "Нархи йигирма беш доллар",
            "5-синф": "бешинчи синф",
            "Сана: 12.03.2026": "Сана: икки минг йигирма олтинчи йил ўн иккинчи март",
            "АҚШ": "Америка Қўшма Штатлари",
            "Ҳарорат -3°C": "Ҳарорат минус уч даража",
            "1991 йил 31 августда": "минг тўққиз юз тўқсон биринчи йил ўттиз биринчи августда",
        })


if __name__ == "__main__":
    unittest.main()
