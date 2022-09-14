import math
import os
import random
import subprocess

PARTICIPANTS = "participants.txt"
PDF_DIR = "jobs_pdf"
JOBS_FRONT = "jobs_front.tex"
JOBS_BACK = "jobs_back.tex"
JOBS_SRC = "jobs.tex"
JOBS_PER_LINE = 3


def format_job(murderer, target):
    return f"\\job{{{murderer}}}{{{target}}}"


def format_back(murderer):
    return f"\\jobback{{{murderer}}}"


def build_cover_line(jobs):
    # pad murderers
    murderers = [jobs[i][0] if i < len(jobs) else "" for i in range(JOBS_PER_LINE)]
    # cover has to be reversed for the double page printing stuff
    murderers.reverse()
    line = ""
    for murderer in murderers:
        line += f"{format_back(murderer)}\n"
    return line


def main():
    # read all participants
    with open(PARTICIPANTS, "r") as f:
        lines = f.readlines()
    # remove all line breaks
    lines = [line.replace("\n", "") for line in lines]
    # shuffle all the children
    random.shuffle(lines)

    # now every participant in a line kills the participant from the next line
    jobs = []
    for i in range(len(lines)):
        murderer = lines[i]
        target = lines[(i + 1) % len(lines)]
        jobs.append((murderer, target))
        
    # build string for job front
    jobs_str = ""
    for murderer, target in jobs:
        jobs_str += f"{format_job(murderer, target)}\n"
    
    # build string for job back
    cover_str = ""
    n_lines = math.ceil(len(jobs) / JOBS_PER_LINE)
    for i in range(n_lines):
        start = i * JOBS_PER_LINE
        end = min((i + 1) * JOBS_PER_LINE, len(jobs))
        line_jobs = jobs[start:end]
        cover_str += build_cover_line(line_jobs)

    # write the jobs
    with open(os.path.join(PDF_DIR, JOBS_FRONT), "w") as f:
        f.write(jobs_str)
    with open(os.path.join(PDF_DIR, JOBS_BACK), "w") as f:
        f.write(cover_str)
    # generate the pdf
    cmd = ["pdflatex", "-interaction", "nonstopmode", f"-output-directory={PDF_DIR}", os.path.join(PDF_DIR, JOBS_SRC)]
    proc = subprocess.Popen(cmd)
    proc.communicate()


if __name__ == "__main__":
    main()
