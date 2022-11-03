#!/usr/bin/env python3

import argparse
import validators
from custom_log import logging

from catalog_parser import CatalogParser


def get_html(page: str) -> str:
    html = None
    if validators.url(page):
        raise NotImplementedError("URLs are not yet supported")
    else:
        logging.debug("Is not a URL")
        f = open(page, 'r')
        html = f.read()
        f.close()
    return html


def parse_html(html: str):
    html_parser = CatalogParser()
    html_parser.feed(html)
    print([str(course) for course in html_parser.courses])


def main():
    parser = argparse.ArgumentParser(
        prog='course_explorer',
        description='Web scraper and analyzer for university course catalogs.',
        epilog='For more information, please see the README.')
    parser.add_argument(
        'page', help="file path or URL of course catalog to scrape")
    log_level_group = parser.add_mutually_exclusive_group()
    log_level_group.add_argument('-q', '--quiet', action='store_true')
    log_level_group.add_argument('-v', '--verbose', action='count',
                                 default=0, help="enable verbose output. "
                                 "-v enables debug output, "
                                 "-vv enables trace output")
    args = parser.parse_args()

    level = None
    if args.quiet:
        level = "CRITICAL"
    else:
        match args.verbose:
            case 0:
                level = "INFO"
            case 1:
                level = "DEBUG"
            case _:
                level = "TRACE"
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')

    html = get_html(args.page)
    parse_html(html)


if __name__ == "__main__":
    main()
