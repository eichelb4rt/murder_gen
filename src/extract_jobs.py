import os
import re
import string
import pandas as pd
from PyPDF2 import PdfReader

from jobs import Job


BOTCHED_NAMES_FILE = "botched_names.csv"


def remove_non_ascii(text: str) -> str:
    ALLOWED_CHARS = string.ascii_letters + " \n"
    return "".join(c for c in text if c in ALLOWED_CHARS)


def transform_botched(name: str, botch_map: dict[str, str]) -> str:
    if name in botch_map:
        return botch_map[name]
    return name


def extract_jobs_from_pdf(pdf_path: str) -> list[Job]:
    # import the botch map
    if os.path.isfile(BOTCHED_NAMES_FILE):
        botched_names: pd.DataFrame = pd.read_csv(BOTCHED_NAMES_FILE)
        botch_map = {row['botched_name']: row['clear_name'] for _, row in botched_names.iterrows()}
    else:
        botch_map = {}
    reader = PdfReader(pdf_path)
    # we need only half the pages to extract all the jobs, because the other half of the pages are the back side to the first half of the pages
    killers_and_targets = "\n".join([page.extract_text() for page in reader.pages[::2]])
    # clean all non-ascii chars because they lead to trouble
    killers_and_targets = remove_non_ascii(killers_and_targets)
    # put all "Killer" tags in a new line that were not in a new line before
    killers_and_targets = re.sub(r'\n(.+)Killer', r'\n\1\nKiller', killers_and_targets)
    # remove all empty jobs
    killers_and_targets = re.sub(r'\nKiller\nTarget', '', killers_and_targets)
    # iterate over the lines and save them as jobs
    jobs: list[Job] = []
    lines = killers_and_targets.splitlines()
    killer_lines: list[str] = []
    target_lines: list[str] = []
    for i, line in enumerate(lines):
        # valid job pdfs have to have "Killer" at the start
        if i == 0 and line != "Killer":
            print(f"not a valid job pdf: {pdf_path}")
            exit(1)
        # switch building mode depending on what we see
        if line == "Killer":
            # after the first line, if we encounter a new "Killer", then we have to save the last job
            if i > 0:
                killer = transform_botched(" ".join(killer_lines), botch_map)
                target = transform_botched(" ".join(target_lines), botch_map)
                jobs.append(Job(killer, target))
                killer_lines = []
                target_lines = []
            building = "killer"
            continue
        # if we find a "Target" tag, we continue building the target
        if line == "Target":
            building = "target"
            continue
        # if we encounter a line that is not a valid tag, we just add it to whatever we're building
        if building == "killer":
            killer_lines.append(line)
            continue
        if building == "target":
            target_lines.append(line)
            continue
    # append the last job
    killer = transform_botched(" ".join(killer_lines), botch_map)
    target = transform_botched(" ".join(target_lines), botch_map)
    jobs.append(Job(killer, target))
    return jobs


def main():
    jobs = extract_jobs_from_pdf("jobs_pdf/jobs.pdf")
    print(jobs)


if __name__ == "__main__":
    main()
