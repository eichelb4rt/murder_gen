from dataclasses import dataclass


@dataclass
class Job:
    killer: str
    target: str

@dataclass
class JobList:
    name: str
    jobs: list[Job]