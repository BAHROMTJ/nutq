"""Command-line interface: nutq <command> --lang <code> [text]"""

import argparse
import sys

from . import __version__, clean, convert, languages, normalize, number_to_words


def _read_text(args):
    if args.text:
        return " ".join(args.text)
    return sys.stdin.read().rstrip("\n")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="nutq",
        description="Script conversion and text normalization for Tajik, Persian, Dari and Uzbek.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    conv = sub.add_parser("convert", help="convert between scripts")
    conv.add_argument("--lang", "-l", required=True)
    conv.add_argument("--to", "-t", required=True, help="Cyrl, Latn or Arab")
    conv.add_argument("--from", dest="source", help="source script (detected if omitted)")
    conv.add_argument("text", nargs="*")

    for name, help_text in (("normalize", "numbers, dates and money to words"),
                            ("clean", "fix look-alike characters")):
        cmd = sub.add_parser(name, help=help_text)
        cmd.add_argument("--lang", "-l", required=True)
        cmd.add_argument("text", nargs="*")

    num = sub.add_parser("number", help="number to words")
    num.add_argument("--lang", "-l", required=True)
    num.add_argument("--ordinal", action="store_true")
    num.add_argument("--script", help="output script")
    num.add_argument("value", type=int)

    sub.add_parser("languages", help="list supported languages")

    args = parser.parse_args(argv)
    if args.command == "convert":
        print(convert(_read_text(args), args.lang, to=args.to, source=args.source))
    elif args.command == "normalize":
        print(normalize(_read_text(args), args.lang))
    elif args.command == "clean":
        print(clean(_read_text(args), args.lang))
    elif args.command == "number":
        print(number_to_words(args.value, args.lang, ordinal=args.ordinal, script=args.script))
    elif args.command == "languages":
        for lang in languages():
            print(f"{lang.code:6} {lang.name:8} {lang.native_name:10} {', '.join(lang.scripts):16} {lang.status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
