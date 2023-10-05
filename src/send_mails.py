import os
import glob
import pandas as pd
from pathlib import Path
from collections import defaultdict

from jobs import JobList
from extract_jobs import extract_jobs_from_pdf

MAILS_FILE = "mails.csv"
JOB_LISTS_DIR = "all_job_lists"

def extract_job_lists() -> list[JobList]:
    """Extract all the job lists from the pdfs in the job list directory."""

    job_lists: list[JobList] = []
    for job_file in glob.glob(f"{JOB_LISTS_DIR}/*.pdf"):
        name = Path(job_file).stem
        jobs = extract_jobs_from_pdf(job_file)
        job_lists.append(JobList(name, jobs))
    return job_lists


def extract_missions(job_lists: list[JobList]) -> dict[str, list[tuple[str, str]]]:
    """Converts the job lists to a dictionary which maps from killers to tuples which each include a job list name and the respective target in that job list."""
    
    killer_to_missions: dict[str, list[tuple[str, str]]] = defaultdict(lambda: [])
    for job_list in job_lists:
        for job in job_list.jobs:
            killer_to_missions[job.killer].append((job_list.name, job.target))
    return dict(killer_to_missions)


def is_concurrent(mails: pd.DataFrame, missions: dict[str, list[tuple[str, str]]]) -> bool:
    """Checks if the people mentioned in the mails csv and the people mentioned in the missions are concurrent."""
    
    people_in_mails = set(mails["name"])
    people_in_missions = set(missions.keys())
    return people_in_mails == people_in_missions


def build_mail(killer: str, missions: list[tuple[str, str]]) -> str:
    message = f"Hallo {killer},\n\nhier nochmal die Aufträge, die du am Anfang des Mörderspiels bekommen hast:\n\n"
    for job_list_name, target in missions:
        message += f"Kreis {job_list_name}: {target}\n"
    message += "\nLG die Organisation der Mörderspiels"
    return message


def main():
    # read the participant mails
    if not os.path.isfile(MAILS_FILE):
        print(f"You still need to create '{MAILS_FILE}'!")
        exit(1)
    mails: pd.DataFrame = pd.read_csv(MAILS_FILE)
    # extract all the job lists from the pdfs
    job_lists = extract_job_lists()
    killer_to_missions = extract_missions(job_lists)
    assert is_concurrent(mails, killer_to_missions), f"mails and missions are not concurrent:\nMails: {set(mails['name'])}\nMissions: {set(killer_to_missions.keys())}"
    print(build_mail("Person B", killer_to_missions["Person B"]))


if __name__ == "__main__":
    main()
