# Murder generator

Generates a list of jobs for the game [murder](http://www.games-wiki.org/wiki/Assassin_game/). Uses `pdflatex` to generate a pdf for the job cutouts.

## Usage

Generate Jobs: Put participants in `participants.txt`, then `python gen_jobs.py`. You can then find all the jobs in `jobs_pdf/jobs.pdf`.

## Printing

You can print the inside of the jobs (first half of the pdf), then print the covers onto the inside jobs.
This way, the result is a bunch of little cards, that you can fold at the horizontal line, so that the distributers of the jobs don't know their content.
