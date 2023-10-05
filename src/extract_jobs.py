import re
import glob
from PyPDF2 import PdfReader
from job import Job


def extract_jobs_from_pdf(pdf_path: str) -> list[Job]:
    reader = PdfReader(pdf_path)
    # we need only half the pages to extract all the jobs, because the other half of the pages are the back side to the first half of the pages
    useful_pages = reader.pages[:len(reader.pages) // 2]
    useful_text = "\n".join([page.extract_text() for page in useful_pages])
    # put all "Killer" tags in a new line that were not in a new line before
    killers_and_targets = re.sub(r'\n(.+)Killer', r'\n\1\nKiller', useful_text)
    # remove all empty jobs
    killers_and_targets = re.sub(r'\nKiller\nTarget', '', killers_and_targets)
    # iterate over the lines and save them as jobs
    jobs: list[Job] = []
    killer: str = ""
    target: str = ""
    for i, line in enumerate(killers_and_targets.splitlines()):
        # if we find a new "Killer" line, we can append the current killer
        if line == "Killer":
            jobs.append(Job(killer, target))
        if line == "Target":
            print("end")


def main():
    extract_jobs_from_pdf("jobs_pdf/jobs.pdf")


if __name__ == "__main__":
    main()
