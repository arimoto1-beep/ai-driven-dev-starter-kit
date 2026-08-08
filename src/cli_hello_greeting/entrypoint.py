import argparse
import sys

try:
    from cli_hello_greeting.features.greeting import create_greeting
except ModuleNotFoundError:
    from features.greeting import create_greeting


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a greeting message.")
    parser.add_argument("--name", required=True, help="Name to greet.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args(argv)
    greeting = create_greeting(args.name)
    print(greeting)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
