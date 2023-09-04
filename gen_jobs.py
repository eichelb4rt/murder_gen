import math
import os
import random
import subprocess
from dataclasses import dataclass

PARTICIPANTS = "participants.txt"
PDF_DIR = "jobs_pdf"
PDF_NAME = "jobs"
SRC_JOB_LIST = "job_list.tex"
SRC_MAIN = "main.tex"
JOBS_PER_LINE = 3
LINES_PER_PAGE = 4
JOBS_PER_PAGE = JOBS_PER_LINE * LINES_PER_PAGE


@dataclass
class Job:
    murderer: str
    victim: str


EMPTY_JOB = Job("\\hfill", "\\hfill")


def extract_random_jobs(participants_file: str) -> list[Job]:
    # read all participants
    with open(participants_file, "r") as f:
        lines = f.readlines()
    # remove all line breaks
    lines = [line.replace("\n", "") for line in lines]
    # shuffle all the participants
    random.shuffle(lines)
    # now every participant in a line kills the participant from the next line
    return [Job(lines[i], lines[(i + 1) % len(lines)]) for i in range(len(lines))]


def format_front(job: Job) -> str:
    return f"\\job{{{job.murderer}}}{{{job.victim}}}"


def format_back(job: Job) -> str:
    return f"\\jobback{{{job.murderer}}}"


def build_page_front(jobs_in_page: list[Job]) -> str:
    assert len(jobs_in_page) == JOBS_PER_LINE * LINES_PER_PAGE, "Page has to be full (maybe even with empty jobs) to be valid."
    return "\n".join([format_front(job) for job in jobs_in_page]) + "\n\\clearpage"


def build_back_line(jobs_in_line: list[Job]) -> str:
    # back has to be reversed for the double page printing stuff
    return "\n".join([format_back(job) for job in reversed(jobs_in_line)])


def build_page_back(jobs_in_page: list[Job]) -> str:
    assert len(jobs_in_page) == JOBS_PER_PAGE, "Page has to be full (maybe even with empty jobs) to be valid."
    return "\n".join([build_back_line(jobs_in_page[JOBS_PER_LINE * i: JOBS_PER_LINE * (i + 1)]) for i in range(LINES_PER_PAGE)])


def build_page(jobs_in_page: list[Job]) -> str:
    return build_page_front(jobs_in_page) + "\n" + build_page_back(jobs_in_page)


def build_all_pages(jobs: list[Job]) -> str:
    assert len(jobs) % JOBS_PER_PAGE == 0, "Every page has to be full (maybe even with empty jobs) to be valid."
    n_pages = len(jobs) // JOBS_PER_PAGE
    pages = [build_page(jobs[JOBS_PER_PAGE * page_index: JOBS_PER_PAGE * (page_index + 1)]) for page_index in range(n_pages)]
    return "\n".join(pages)


def pad_to_full_pages(jobs: list[Job]) -> list[Job]:
    jobs_over_last_full_page = len(jobs) % JOBS_PER_PAGE
    if jobs_over_last_full_page == 0:
        return jobs
    pad_size = JOBS_PER_PAGE - jobs_over_last_full_page
    return jobs + [EMPTY_JOB] * pad_size


def main():
    # generate the job list content
    jobs = extract_random_jobs(PARTICIPANTS)
    jobs = pad_to_full_pages(jobs)
    jobs_str = build_all_pages(jobs)
    # write the jobs
    with open(os.path.join(PDF_DIR, SRC_JOB_LIST), "w") as f:
        f.write(jobs_str)
    # generate the pdf
    cmd = ["pdflatex", "-interaction", "nonstopmode", f"-output-directory={PDF_DIR}", f"-jobname={PDF_NAME}", os.path.join(PDF_DIR, SRC_MAIN)]
    proc = subprocess.Popen(cmd)
    proc.communicate()


if __name__ == "__main__":
    main()
