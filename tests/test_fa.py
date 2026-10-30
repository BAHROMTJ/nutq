import unittest

import nutq

ZWNJ = "‌"


class NumbersTest(unittest.TestCase):
    def test_cardinals(self):
        cases = {
            0: "صفر", 1: "یک", 11: "یازده", 15: "پانزده", 21: "بیست و یک",
            100: "صد", 125: "صد و بیست و پنج", 200: "دویست", 500: "پانصد",
            1000: "هزار", 1001: "هزار و یک", 1100: "هزار و صد",
            2026: "دو هزار و بیست و شش", 1_000_000: "یک میلیون",
            3_000_015: "سه میلیون و پانزده", -4: "منفی چهار",
        }
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(nutq.number_to_words(number, "fa"), expected)

    def test_ordinals(self):
        cases = {1: "یکم", 2: "دوم", 3: "سوم", 13: "سیزدهم", 23: "بیست و سوم",
                 30: "سی" + ZWNJ + "ام", 100: "صدم", 1000: "هزارم"}
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(nutq.number_to_words(number, "fa", ordinal=True), expected)

    def test_dari_shares_number_words(self):
        self.assertEqual(nutq.number_to_words(2026, "prs"), "دو هزار و بیست و شش")


class CleanTest(unittest.TestCase):
    def test_arabic_letters(self):
        self.assertEqual(nutq.clean("كتابي", "fa"), "کتابی")

    def test_digits_and_tatweel(self):
        self.assertEqual(nutq.clean("سـلام ٢٠٢٦", "fa"), "سلام ۲۰۲۶")

    def test_zwnj(self):
        self.assertEqual(nutq.clean("می" + ZWNJ * 3 + "شود", "fa"), "می" + ZWNJ + "شود")
        self.assertEqual(nutq.clean("کتاب" + ZWNJ + " خوب", "fa"), "کتاب خوب")

    def test_presentation_forms(self):
        self.assertEqual(nutq.clean("ﻻ", "fa"), "لا")


class NormalizeTest(unittest.TestCase):
    def check(self, lang, cases):
        for text, expected in cases.items():
            with self.subTest(lang=lang, text=text):
                self.assertEqual(nutq.normalize(text, lang), expected)

    def test_persian(self):
        self.check("fa", {
            "قیمت ۲۵ دلار است": "قیمت بیست و پنج دلار است",
            "۱۵٪": "پانزده درصد",
            "۲٫۵": "دو ممیز پنج",
            "2.05": "دو ممیز صفر پنج",
            "$3.20": "سه دلار و بیست سنت",
            "ساعت ۱۴:۳۰": "ساعت چهارده و سی دقیقه",
            "۱۴۰۵/۰۱/۱۲": "دوازدهم فروردین هزار و چهارصد و پنج",
            "12.03.2026": "دوازدهم مارس دو هزار و بیست و شش",
            "۲۳م": "بیست و سوم",
            "۱۳۹۰ ه.ش.": "هزار و سیصد و نود هجری شمسی",
            "۱٬۲۵۰": "هزار و دویست و پنجاه",
            "دمای ۳۰°C": "دمای سی درجه",
            "۲۲ بهمن ۱۳۵۷": "بیست و دوم بهمن هزار و سیصد و پنجاه و هفت",
            "نسخه ۱.۲.۳": "نسخه یک نقطه دو نقطه سه",
            "+۹۸ ۹۱۲ ۳۴۵ ۶۷۸۹": "نود و هشت، نهصد و دوازده، سیصد و چهل و پنج، شش هزار و هفتصد و هشتاد و نه",
        })

    def test_dari(self):
        self.check("fa-AF", {
            "۱۵٪": "پانزده فیصد",
            "۲٫۵": "دو اعشاریه پنج",
            "۱۴۰۵/۰۱/۱۲": "دوازدهم حمل هزار و چهارصد و پنج",
            "12.03.2026": "دوازدهم مارچ دو هزار و بیست و شش",
            "۱۰۰ ؋": "صد افغانی",
            "۲۸ اسد": "بیست و هشتم اسد",
        })


if __name__ == "__main__":
    unittest.main()
