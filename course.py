#!/usr/bin/env python3

from enum import Enum


class Course:
    Level = Enum('Level', ['Undergraduate', 'Graduate'])

    def __init__(self) -> None:
        self.name = None
        self.description = None
        self.levels = None

        self.subject = None
        self.number = None
        self.title = None
        self.prereqs = None

    def __str__(self) -> str:
        return str({"Title": self.title, "Prerequisites": self.prereqs})
