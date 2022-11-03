#!/usr/bin/env python3

from html.parser import HTMLParser
from course import Course

import logging


class CatalogParser(HTMLParser):
    TABLE_SUMMARY = 'This table lists all course detail for the selected term.'
    LEVELS_TEXT = 'Levels:'

    def __init__(self, *, convert_charrefs: bool = ...) -> None:
        # Whether we are currently parsing the <table> element containing the
        # courses. There are multiple tables on the page.
        self.is_in_course_table = False
        # The course that we are currently constructing. The lifetime of this
        # object is bound to the two <tr> elements within the course table.
        self.tmp_course = None
        # Whether we are currently parsing the <tr> elements corresponding to a
        # course. This is as opposed to being in the state of parsing any other
        # <tr> elments, or not parsing any <tr> elements at all.
        self.is_in_course = False
        # Whether we are parsing the *last* <tr> element corresponding to a
        # course, and should therefore finalize the course object.
        self.is_last_in_course = False
        # Sorted by course number (ascending)
        self.courses = []
        # See self.handle_data().
        self.is_waiting_for_levels = False
        super().__init__(convert_charrefs=convert_charrefs)

    def handle_starttag(self, tag: str,
                        attrs: list[tuple[str, str | None]]) -> None:
        logging.trace('START <{}>'.format(tag))

        # We are interested in the following table:
        #  <table
        #   CLASS="datadisplaytable"
        #   SUMMARY="This table lists all course detail for the selected term."
        #   WIDTH="100%"
        #  >
        if not self.is_in_course_table:
            if tag == 'table':
                matching_summary = (
                    attr
                    for attr in attrs
                    if attr[0] == 'summary' and
                    attr[1] == self.TABLE_SUMMARY
                )
                if (next(matching_summary, None) != None):
                    logging.debug("Entering course table.")
                    self.is_in_course_table = True
            return

        # At this point in the method, we are now inside the class table.
        if tag == 'tr':
            if self.is_in_course:
                # There are only two <tr>s per course, so we are done after
                # this one. Of course, we still have more data to read within
                # this <tr>, but this state variable only concerns tag openings
                # and closings, ignoring the text in the middle.
                self.is_last_in_course = True
                self.is_in_course = False
                return
            if self.tmp_course != None:
                # Ellucian doesn't close half of their <tr>s...
                logging.debug(
                    "Attempted to start a new row with a course in progress. "
                    "Force closing the last row.")
                self.handle_endtag('tr')
            logging.debug("Entering course row.")
            assert self.tmp_course == None
            self.tmp_course = Course()
            self.is_in_course = True

    def handle_endtag(self, tag: str) -> None:
        logging.trace('END <{}>'.format(tag))

        # Assume that there is not a table nested within the course table.
        if tag == 'table':
            logging.debug("Exiting course table.")
            # Same edge case as above.
            if self.tmp_course != None:
                logging.debug(
                    "Attempted to end the table with a course in progress. "
                    "Force closing the last row.")
                self.handle_endtag('tr')
            self.is_in_course_table = False

        elif tag == 'tr' and self.is_last_in_course and self.is_in_course_table:
            logging.debug("Exiting course row.")
            # If we encountered a "Levels: " and then try to exit the course
            # row, something is wrong.
            assert not self.is_waiting_for_levels
            self.tmp_course.initialize()
            self.courses.append(self.tmp_course)
            self.tmp_course = None
            self.is_last_in_course = False

    def handle_data(self, data: str) -> None:
        logging.trace("IN ELEMENT <{}>: {}".format(self.lasttag, data.strip()))
        # If we're not currently reading a course, there's nothing to do.
        if self.tmp_course == None:
            return
        assert isinstance(self.tmp_course, Course)

        data = data.strip()
        # There are a lot of blank lines that we have to ignore.
        if not data:
            return
        # The first data is the course title.
        if self.tmp_course.title == None:
            logging.debug("Reading course title: \"{}\"".format(data))
            self.tmp_course.title = data
            return
        # The next is the course description.
        if self.tmp_course.description == None:
            # If we hit the levels text sooner than expected.
            if data == self.LEVELS_TEXT:
                logging.warning("The course \"{}\" doesn't seem to have a"
                                "description. Leaving empty."
                                .format(self.tmp_course.title))
                self.tmp_course.description = ""
            else:
                logging.debug(
                    "Reading course description: \"{}\"".format(data))
                self.tmp_course.description = data
                return
        if data == self.LEVELS_TEXT:
            logging.debug("Preparing to read course levels.")
            self.is_waiting_for_levels = True
            return
        if self.is_waiting_for_levels:
            logging.debug("Reading course levels: \"{}\".".format(data))
            self.tmp_course.levels = [Course.Level[level]
                                      for level in data.split(', ')]
            self.is_waiting_for_levels = False
            return

        raise ValueError("I'm not sure what to do with this (inside <{}>): \"{}\"".format(
            self.lasttag, data))
