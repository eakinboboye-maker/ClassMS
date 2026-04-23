import argparse
import subprocess
import sys


def run_command(command: list[str]):
    result = subprocess.run(command)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Backend management helper")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("runserver")
    subparsers.add_parser("migrate")
    subparsers.add_parser("test")
    subparsers.add_parser("seed")
    subparsers.add_parser("worker")
    subparsers.add_parser("expiry")

    args = parser.parse_args()

    if args.command == "runserver":
        run_command(["uvicorn", "app.main:app", "--reload"])
    elif args.command == "migrate":
        run_command(["alembic", "upgrade", "head"])
    elif args.command == "test":
        run_command(["pytest"])
    elif args.command == "seed":
        run_command([sys.executable, "seed_data.py"])
    elif args.command == "worker":
        run_command([sys.executable, "-m", "app.workers.grading_jobs", "--pending", "--limit", "20"])
    elif args.command == "expiry":
        run_command([sys.executable, "-m", "app.workers.grading_jobs", "--expiry-check"])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
