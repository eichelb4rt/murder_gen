# Murder generator

Generates a list of jobs for the game [murder](http://www.games-wiki.org/wiki/Assassin_game/). Uses `pdflatex` to generate a pdf for the job cutouts.
You can find an example of generated jobs in [`example.pdf`](./example.pdf).

## Usage

Put participants in `participants.txt` (like in [`participants-template.txt`](./participants-template.txt)), then `python gen_jobs.py`.
You can then find all the jobs in `jobs_pdf/jobs.pdf`.

## Printing

You should print the jobs double sided.
This way, the result is a bunch of little cards.
You can fold the cards twice using the horizontal line as illustrated below, so that the distributers of the jobs don't know their content.

![How to fold the cards](how_to_fold.png)
