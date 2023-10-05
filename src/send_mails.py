import os
import pandas as pd

MAILS_FILE = "mails.csv"

def main():
    # read the participant mails
    if not os.path.isfile(MAILS_FILE):
        print(f"You still need to create '{MAILS_FILE}'!")
        exit(1)
    mails = pd.read_csv(MAILS_FILE)

if __name__ == "__main__":
    main()