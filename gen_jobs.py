import os
import random
import subprocess

PARTICIPANTS = "participants.txt"
PDF_DIR = "jobs_pdf"
JOB_LIST = "job_list.tex"
JOBS_SRC = "jobs.tex"


def main():
    # read all children
    with open(PARTICIPANTS, "r") as f:
        lines = f.readlines()
    # remove all line breaks
    lines = [line.replace("\n", "") for line in lines]
    # shuffle all the children
    random.shuffle(lines)

    # now every participant in a line kills the participant from the next line
    jobs = ""
    for i in range(len(lines)):
        murderer = lines[i]
        target = lines[(i + 1) % len(lines)]
        job = format_job(murderer, target)
        jobs += f"{job}\n"

    # write the jobs
    with open(os.path.join(PDF_DIR, JOB_LIST), "w") as f:
        f.write(jobs)
    # generate the pdf
    cmd = ["pdflatex", "-interaction", "nonstopmode", f"-output-directory={PDF_DIR}", os.path.join(PDF_DIR, JOBS_SRC)]
    proc = subprocess.Popen(cmd)
    proc.communicate()


def format_job(murderer, target):
    global delim
    return f"\\job{{{murderer}}}{{{target}}}"


if __name__ == "__main__":
    main()
