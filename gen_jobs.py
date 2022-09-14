import random

children_file = "participants.txt"
jobs_file = "jobs.txt"
delim = "================================"

def main():
    global children_file, jobs_file
    # read all children
    with open(children_file, "r") as f:
        lines = f.readlines()
    # remove all line breaks
    lines = [line.replace("\n", "") for line in lines]
    # shuffle all the children
    random.shuffle(lines)#
    # now every child in a line kills the child from the next line
    jobs = ""
    for i in range(len(lines)):
        murderer = lines[i]
        target = lines[(i + 1) % len(lines)]
        job = format_job(murderer, target)
        jobs += f"{job}\n"
    # write the jobs
    with open(jobs_file, "w") as f:
        f.write(jobs)

def format_job(murderer, target):
    global delim
    return f"{delim}\nKiller:\t{murderer}\nZiel:\t{target}\n{delim}\n"

if __name__ == "__main__":
    main()