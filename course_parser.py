#!/usr/bin/env python3

import logging
from typing import Tuple

from course import Course
from bing_subjects import subjects, prog_course_and_title, prog_course

# Sample descriptions:

# Prerequisite: none.  Offered in the Fall semester.

# Prerequisite: none Offered every semester. 4 credits

# Prerequisite: Math 225 (May be taken concurrently. )  (All prerequisites must have a grade of C- or better).Offered every semester. 4 credits

# Prerequisites: HARP 170 and enrollment in Freshman Research Immersion (FRI) program (All prerequisites must have a grade of C- or better).  Offered in the Spring semester.

# Prerequisite MATH 225 that may be taken concurrently. CS 110, CS Majors may request a waiver from the Undergraduate Director based on prior programming experience (All prerequisites must have a grade of C- or better)

# Prerequisite: CS 110,CS Majors may request a waiver from the Undergraduate Director based on prior programming experience.  Math 225 (All prerequisites must have a grade of C- or better). Offered every semester.


def parse_name(name: str) -> Tuple[str, str, str]:
    match = prog_course_and_title.match(name)
    if not match:
        raise ValueError("Unable to parse course name \"{}\"".format(name))
    assert len(match.groups()) == 3
    return match.groups()


def parse_prereqs(desc: str) -> list[Tuple[str, str]]:
    # TODO: account for "or"
    matches = prog_course.findall(desc)
    if not matches:
        return []
    return matches


def parse_course(course: Course):
    course.subject, course.number, course.title = parse_name(course.name)
    course.prereqs = parse_prereqs(course.description)
