#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from pathlib import Path
from sys import stdout
import argparse
from loguru import logger
import bs4
import nest_asyncio; nest_asyncio.apply()
from playwright.sync_api import sync_playwright
#}}}


# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def writehtml(fname, html):
    with open(fname, 'w') as f:
        f.write(html)
    f.close()
# }}}


# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/scrape.log")

    logger.info('setting up session')
    pw = sync_playwright().start()
    chrome = pw.chromium.launch(headless=False)
    page = chrome.new_page()

    logger.info('accessing page content')
    page.goto(args.url)
    content = page.content()

    logger.info('writing html data')
    writehtml(fname=args.output, html=content)

    logger.info('done')
# }}}

# done.
