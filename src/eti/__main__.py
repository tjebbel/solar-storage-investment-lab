"""Command line: python -m eti [--db PATH] [--out DIR]"""
import argparse
import sys

from .pipeline import run


def main(argv=None):
    ap = argparse.ArgumentParser(prog="eti", description="Solar + storage investment analytics")
    ap.add_argument("--db", default="data/eti.db")
    ap.add_argument("--out", default="reports")
    ap.add_argument("--source", choices=["synthetic", "live"], default="synthetic",
                    help="'live' downloads Dutch prices and generation from the Energy-Charts API")
    ap.add_argument("--year", type=int, default=2024)
    ap.add_argument("--no-figures", action="store_true")
    args = ap.parse_args(argv)
    res = run(args.db, args.out, source=args.source, year=args.year, figures=not args.no_figures)
    print(f"Solar IRR {res['solar']['irr']:.1%} | capture rate {res['market']['capture_rate_solar']:.3f} "
          f"| portfolio IRR {res['portfolio']['irr']:.1%} | source {args.source} {args.year} -> {args.out}/results.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
