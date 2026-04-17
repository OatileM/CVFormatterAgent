"""CLI entry point for the CV Formatter Agent.

Usage:
    python main.py <cv_path> <job_spec> [--output-dir OUTPUT_DIR]

Arguments:
    cv_path     Path to the CV file (PDF, DOCX, or TXT).
    job_spec    Path to a text file containing the job specification, OR the
                raw job specification text inline.
    --output-dir
                Directory for output files (default: "output").
"""

from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

import session
from agent import create_agent

# Load environment variables from .env file
load_dotenv()


def main() -> None:
    """Parse CLI arguments and run the CV Formatter Agent."""
    parser = argparse.ArgumentParser(
        description="Reformat a CV for ATS compatibility using an AI agent.",
    )
    parser.add_argument(
        "cv_path",
        help="Path to the CV file (PDF, DOCX, or TXT).",
    )
    parser.add_argument(
        "job_spec",
        help=(
            "Path to a text file containing the job specification, "
            "or the raw job specification text inline."
        ),
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for output files (default: 'output').",
    )

    args = parser.parse_args()

    cv_path: str = args.cv_path
    job_spec_arg: str = args.job_spec
    output_dir: str = args.output_dir

    # If job_spec looks like an existing file path, read its contents.
    if os.path.isfile(job_spec_arg):
        with open(job_spec_arg, encoding="utf-8") as fh:
            job_spec = fh.read()
    else:
        job_spec = job_spec_arg

    agent = create_agent()

    prompt = (
        f"Format the CV at '{cv_path}' for the following job specification:\n\n"
        f"{job_spec}\n\n"
        f"Output files to: {output_dir}"
    )

    response = agent(prompt)
    print(response)


if __name__ == "__main__":
    main()
