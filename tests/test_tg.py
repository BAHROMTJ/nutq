import unittest

import nutq


def words(n, ordinal=False):
    return nutq.number_to_words(n, "tg", ordinal=ordinal)


class NumbersTest(unittest.TestCase):
    def test_cardinals(self):
        cases = {
            0: "сифр", 1: "як", 11: "ёздаҳ", 19: "нуздаҳ", 21: "бисту як",
            30: "сӣ", 32: "сиву ду", 100: "сад", 125: "саду бисту панҷ",
            909: "нӯҳсаду нӯҳ", 1000: "як ҳазор", 1001: "як ҳазору як",
            2026: "ду ҳазору бисту шаш", 2500: "ду ҳазору панҷсад",
            1_000_000: "як миллион", 3_000_015: "се миллиону понздаҳ",
            -7: "минус ҳафт",
        }
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(words(number), expected)

    def test_ordinals(self):
        cases = {1: "якум", 2: "дуюм", 3: "сеюм", 4: "чорум", 10: "даҳум",
                 21: "бисту якум", 30: "сиюм", 100: "садум"}
        for number, expected in cases.items():
            with self.subTest(number=number):
                self.assertEqual(words(number, ordinal=True), expected)

    def test_other_scripts(self):
        self.assertEqual(nutq.number_to_words(25, "tg", script="Latn"), "bistu panj")
        self.assertEqual(nutq.number_to_words(2026, "tg", script="Arab"), "دو هزار و بیست و شش")

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            words(1.5)
        with self.assertRaises(TypeError):
            words(True)
        with self.assertRaises(ValueError):
            words(0, ordinal=True)
        with self.assertRaises(ValueError):
            words(10 ** 18)


class LatinTest(unittest.TestCase):
    def latin(self, text):
        return nutq.convert(text, "tg", to="Latn")

    def test_to_latin(self):
        self.assertEqual(self.latin("Тоҷикистон"), "Tojikiston")
        self.assertEqual(self.latin("Хуҷанд"), "Khujand")
        self.assertEqual(self.latin("ҒАФУРОВ"), "GHAFUROV")
        self.assertEqual(self.latin("забони тоҷикӣ"), "zaboni tojikī")

    def test_round_trip(self):
        for word in ["Тоҷикистон", "Душанбе", "Хуҷанд", "Ғафуров", "Қӯрғонтеппа", "шаҳр"]:
            with self.subTest(word=word):
                self.assertEqual(nutq.convert(self.latin(word), "tg", to="Cyrl"), word)

    def test_non_letters_untouched(self):
        self.assertEqual(self.latin("2026, ok!"), "2026, ok!")


class ArabicTest(unittest.TestCase):
    def arabic(self, text):
        return nutq.convert(text, "tg", to="Arab")

    def test_letter_rules(self):
        # Words the rules alone spell correctly (no word list entry).
        cases = {
            "нон": "نان", "шаб": "شب", "барф": "برف", "оташ": "آتش", "озод": "آزاد",
            "ном": "نام", "дарё": "دریا", "кӯҳ": "کوه", "рӯз": "روز", "сол": "سال",
            "Самарқанд": "سمرقند", "Рӯдакӣ": "رودکی", "панҷ": "پنج", "одам": "آدم",
            "хона": "خانه", "мактаб": "مکتب", "шаҳр": "شهر", "ҷаҳон": "جهان",
            "як": "یک", "Русия": "روسیه", "аммо": "اما", "хеле": "خیلی",
        }
        for cyrillic, arabic in cases.items():
            with self.subTest(word=cyrillic):
                self.assertEqual(self.arabic(cyrillic), arabic)

    def test_word_list(self):
        cases = {"Тоҷикистон": "تاجیکستان", "китоб": "کتاب", "дил": "دل",
                 "ки": "که", "ва": "و", "Душанбе": "دوشنبه", "илм": "علم"}
        for cyrillic, arabic in cases.items():
            with self.subTest(word=cyrillic):
                self.assertEqual(self.arabic(cyrillic), arabic)

    def test_suffixes(self):
        self.assertEqual(self.arabic("китобҳо"), "کتاب‌ها")
        self.assertEqual(self.arabic("Тоҷикистонро"), "تاجیکستان را")
        self.assertEqual(self.arabic("забони тоҷикӣ"), "زبان تاجیکی")
        self.assertEqual(self.arabic("хонаи калон"), "خانه‌ی کلان")

    def test_comparatives(self):
        self.assertEqual(self.arabic("ширинтар"), "شیرین\u200cتر")
        self.assertEqual(self.arabic("калонтарин"), "کلان\u200cترین")
        self.assertEqual(self.arabic("хубтар"), "خوب\u200cتر")
        self.assertEqual(self.arabic("бештар"), "بیشتر")
        self.assertEqual(self.arabic("дафтар"), "دفتر")
        self.assertEqual(self.arabic("духтар"), "دختر")

    def test_verbs(self):
        self.assertEqual(self.arabic("мешавад"), "می‌شود")
        self.assertEqual(self.arabic("намешавам"), "نمی\u200cشوم")
        self.assertEqual(self.arabic("мева"), "میوه")  # not a verb

    def test_punctuation_and_digits(self):
        self.assertEqual(self.arabic("Салом, дӯстон!"), "سلام، دوستان!")
        self.assertEqual(self.arabic("2,5 ё 10?"), "۲٫۵ یا ۱۰؟")

    def test_from_latin(self):
        self.assertEqual(nutq.convert("Dushanbe", "tg", to="Arab"), "دوشنبه")

    def test_arabic_to_cyrillic_experimental(self):
        cyrillic = lambda text: nutq.convert(text, "tg", to="Cyrl")
        self.assertEqual(cyrillic("تاجیکستان"), "Тоҷикистон")
        self.assertEqual(cyrillic("کتاب‌ها"), "китобҳо")
        self.assertEqual(cyrillic("آب و نان"), "об ва нон")
        self.assertEqual(cyrillic("سلام، ۲۰۲۶"), "салом, 2026")


class CleanTest(unittest.TestCase):
    def test_clean(self):
        self.assertEqual(nutq.clean("Тoҷик", "tg"), "Тоҷик")
        self.assertEqual(nutq.clean("Hello, дунё", "tg"), "Hello, дунё")
        self.assertEqual(nutq.clean("һафта", "tg"), "ҳафта")
        self.assertEqual(nutq.clean("тоҷикӣ", "tg"), "тоҷикӣ")


class NormalizeTest(unittest.TestCase):
    def check(self, cases):
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(nutq.normalize(text, "tg"), expected)

    def test_numbers(self):
        self.check({
            "5 китоб": "панҷ китоб",
            "1 000 000 нафар": "як миллион нафар",
            "2,5 кг": "ду бутуну панҷ даҳум килограмм",
            "-7 дараҷа": "минус ҳафт дараҷа",
            "соли 2020-2026": "соли ду ҳазору бист-ду ҳазору бисту шаш",
            "10км": "даҳ километр",
        })

    def test_ordinals(self):
        self.check({"синфи 5-ум": "синфи панҷум", "2-юми март": "дуюми март"})

    def test_dates_and_times(self):
        self.check({
            "12.03.2026": "дувоздаҳуми марти соли ду ҳазору бисту шаш",
            "2026-01-01": "якуми январи соли ду ҳазору бисту шаш",
            "Соати 14:30": "Соати чордаҳу сӣ дақиқа",
            "дар 9:00": "дар соати нӯҳ",
        })

    def test_money_and_percent(self):
        self.check({
            "Нархи 25 $ аст": "Нархи бисту панҷ доллар аст",
            "$2.50": "ду доллару панҷоҳ сент",
            "100 смн": "сад сомонӣ",
            "12,30 смн": "дувоздаҳ сомониву сӣ дирам",
            "15% тахфиф": "понздаҳ фоиз тахфиф",
        })

    def test_abbreviations(self):
        self.check({"ҶТ": "Ҷумҳурии Тоҷикистон", "5 млн": "панҷ миллион",
                    "китобҳо ва ғ.": "китобҳо ва ғайра"})

    def test_cleans_first(self):
        self.assertEqual(nutq.normalize("Тoҷик 2", "tg"), "Тоҷик ду")


if __name__ == "__main__":
    unittest.main()
