import os
import sys
import glob
import json
import pandas as pd
from pathlib import Path
from collections import defaultdict

import smtplib
from email.message import EmailMessage

from jobs import JobList
from extract_jobs import extract_jobs_from_pdf


JOB_LISTS_DIR = "all_job_lists"
MAILS_FILE = "mails.csv"
MAIL_CONFIG_FILE = "mail_config.json"


def extract_job_lists() -> list[JobList]:
    """Extract all the job lists from the pdfs in the job list directory."""

    print("Extracting job lists...")
    job_lists: list[JobList] = []
    for job_file in glob.glob(f"{JOB_LISTS_DIR}/*.pdf"):
        name = Path(job_file).stem
        jobs = extract_jobs_from_pdf(job_file)
        job_lists.append(JobList(name, jobs))
        print(f"extracted {name}")
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

    people_in_mails = set(mails['name'])
    people_in_missions = set(missions.keys())
    return people_in_mails == people_in_missions


def build_mail_content(killer: str, missions: list[tuple[str, str]], language="english") -> str:
    if language == "english":
        msg_content = f"Hello {killer},\n\nhere are your jobs for the murder game:\n\n"
        for job_list_name, target in missions:
            msg_content += f"group '{job_list_name}': {target}\n"
        msg_content += "\nSincerely, the organisation team of the murder game"
    elif language == "german":
        msg_content = f"Hallo {killer},\n\nhier nochmal die Aufträge, die du am Anfang des Mörderspiels bekommen hast:\n\n"
        for job_list_name, target in missions:
            msg_content += f"Kreis '{job_list_name}': {target}\n"
        msg_content += "\nLG die Organisation der Mörderspiels" 
    else:
        print(f"unknown language: {language} (supported: english, german)")
        exit(1)
    return msg_content


def send_mails(mails: pd.DataFrame, killer_to_missions: dict[str, list[tuple[str, str]]]):
    # read the mail config
    with open(MAIL_CONFIG_FILE, 'r') as f:
        mail_config = json.load(f)
    # build messages
    messages: list[EmailMessage] = []
    for _, row in mails.iterrows():
            killer, killer_mail = row['name'], row['mail']
            msg = EmailMessage()
            msg['Subject'] = "Murder Jobs"
            msg['From'] = mail_config['sender_mail']
            msg['To'] = killer_mail
            msg_content = build_mail_content(killer, killer_to_missions[killer], language=mail_config['language'])
            msg.set_content(msg_content)
            messages.append(msg)
    # show a sample message
    if len(messages) == 0:
        print("no messages to send, exiting.")
        exit(1)
    print("example mail:\n")
    print(f"from: {msg['From']}\nto: {msg['To']}\nsubject: {msg['Subject']}\n================================\n{msg.get_content()}\n================================")
    # confirm that the sample message is alright
    sys.stdout.write(f"Is this ok? (y/n): ")
    while True:
        choice = input().lower()
        if choice == 'y':
            break
        elif choice == 'n':
            print("Aborting.")
            exit(1)
        else:
            sys.stdout.write("Please respond with 'y' or 'n': ")
    # create the connection to the ssl server
    if mail_config['smtp_version'].lower() == 'ssl':
        server = smtplib.SMTP_SSL(mail_config['smtp_host'], port=mail_config['smtp_port'])
    elif mail_config['smtp_version'].lower() == 'tls':
        server = smtplib.SMTP(mail_config['smtp_host'], port=mail_config['smtp_port'])
        server.ehlo()
        server.starttls()
    else:
        print(f"Unknown smtp version: {mail_config['smtp_version']}")
        exit(1)
    # log into smtp server
    print(f"Logging into '{mail_config['smtp_host']}' as '{mail_config['sender_mail']}'...")
    server.login(mail_config['sender_mail'], mail_config['password'])
    # send the messages
    print("Sending mails...")
    for msg in messages:
        server.send_message(msg)
    server.quit()
    print("All mails sent!")


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
    # print(build_mail_content("Person B", killer_to_missions["Person B"]))
    send_mails(mails, killer_to_missions)


if __name__ == "__main__":
    main()
