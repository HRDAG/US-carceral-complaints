#!/usr/bin/env python3
# vim: set ts=4 sts=0 sw=4 si fenc=utf-8 et:
# vim: set fdm=marker fmr={{{,}}} fdl=0 foldcolumn=4:
# Authors:     BP
# Maintainers: BP
# Copyright:   2024, HRDAG, GPL v2 or later
# =========================================

# ---- dependencies {{{
from time import sleep
import argparse
from loguru import logger
import pandas as pd
import bs4
import nest_asyncio; nest_asyncio.apply()
from playwright.sync_api import sync_playwright
#}}}


# newline separates facilities by type (security-level, inpatient, etc)
BYNAME = [
    'Lawrence Correctional Center',
    'Menard Correctional Center',
    'Pontiac Correctional Center',
    'Stateville Correctional Center',

    'Big Muddy River Correctional',
    'Centralia Correctional Center',
    'Danville Correctional Center',
    'Graham Correctional Center',
    'Graham Reception and',
    'Hill Correctional Center',
    'Menard Medium Security Unit',
    'Pinckneyville Correctional',
    'Pontiac Medium Security Unit',
    'Shawnee Correctional Center',
    'Sheridan Correctional Center',
    'Western Illinois Correctional Center',

    'Clayton Work Camp',
    'Decatur Correctional Center',
    'Dixon Springs Structured',
    'DuQuoin Impact Program (DQIP)',
    'East Moline Correctional',
    'Greene County Work Camp',
    'Jacksonville Correctional',
    'Lincoln Correctional Center',
    'Murphysboro Life Skills Re-',
    'Pittsfield Work Camp',
    'Robinson Correctional Center',
    'Southwestern Illinois Correctional Center',
    'Southwestern Illinois Work',
    'Stateville Minimum Security',
    'Taylorville Correctional',
    'Vandalia Correctional Center',
    'Vienna Correctional Center',

    'Dixon Correctional Center',
    'Joliet Treatment Center',
    'Kewanee Life Skills Re-Entry',
    'Logan Correctional Center',
    'Logan Reception and',

    'Joliet Inpatient Treatment',

    'Crossroads Adult Transition',
    'Fox Valley Adult Transition',
    'North Lawndale ATC',
    'Peoria Adult Transition Center',

    'COMPLETE LISTING OF FACILITIES',
]


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

    facilitypages = {}
    for facilityname in BYNAME:
        try:
            page.get_by_role("link", name=facilityname).click()
        except:
            logger.info(f'ERROR processing {facilityname}')
            page.goto(args.url)
            continue
        sleep(1)
        assert facilityname not in facilitypages.keys(), f"\
        Expecting to have not added {facilityname} yet, but \
        found it in data with keys {facilitypages.keys()}"
        facilitypages[facilityname] = page.content()
        page.goto(args.url)

    # two items for "Illinois River Correctional" are formatted differently than the others
    page.get_by_role("listitem").filter(has_text="Maximum Security Facility").get_by_label(
        "Illinois River Correctional").click()
    facilitypages["Illinois River Correctional - Max"] = page.content()
    page.goto(args.url)
    page.get_by_role("listitem").filter(has_text="Medium Security Facility").get_by_label(
        "Illinois River Correctional").click()
    facilitypages["Illinois River Correctional - Med"] = page.content()
    page.goto(args.url)

    logger.info('formatting extracted page content as dataframe')
    df = pd.DataFrame(facilitypages.items(), columns=['name', 'html'])
    logger.info(df)

    logger.info('writing data')
    df.to_parquet(args.output)

    logger.info('done')
# }}}

# done.
