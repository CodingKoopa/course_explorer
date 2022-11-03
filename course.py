#!/usr/bin/env python3

from custom_log import logging
from enum import Enum


class Course:
    Level = Enum('Level', ['Undergraduate', 'Graduate'])

    def __init__(self) -> None:
        self.title = None
        self.description = None
        self.levels = None
        self.initialized = False

    def add_levels(self, levels: str) -> None:
        self.levels = [self.Level[level] for level in levels.split(', ')]

    def initialize(self) -> None:
        # The description is optional.
        if not self.title:
            raise AttributeError("Title not set.")

    def __str__(self) -> str:
        return self.title
