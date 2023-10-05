import re
from PyPDF2 import PdfReader
from jobs import Job


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
    lines = killers_and_targets.splitlines()
    killer_lines: list[str] = []
    target_lines: list[str] = []
    for i, line in enumerate(lines):
        # switch building mode depending on what we see
        if line == "Killer":
            # after the first line, if we encounter a new "Killer", then we have to save the last job
            if i > 0:
                killer = " ".join(killer_lines)
                target = " ".join(target_lines)
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
    killer = " ".join(killer_lines)
    target = " ".join(target_lines)
    jobs.append(Job(killer, target))
    return jobs


def main():
    jobs = extract_jobs_from_pdf("jobs_pdf/jobs.pdf")
    print(jobs)


if __name__ == "__main__":
    main()
