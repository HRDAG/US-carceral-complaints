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
import yaml
import re
import pandas as pd
import bs4
#}}}

# --- support methods --- {{{
def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=None)
    parser.add_argument("--lost", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    assert Path(args.input).exists()
    return args


def setuplogging(logfile):
    logger.add(logfile,
               colorize=True,
               format="<green>{time:YYYY-MM-DD⋅at⋅HH:mm:ss}</green>⋅<level>{message}</level>",
               level="INFO")
    return 1


def readhtml(fname):
    with open(fname, 'r') as f:
        html = f.read()
    return html


def writeyaml(yamlfile, data):
    with open(yamlfile, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
        f.close()
    logger.info(f'{yamlfile} written successfully')
    return 1


def byheader(labels, htmltables):
    if not any(htmltables): return None
    dfs, lost = [], {}
    for i in range(len(htmltables)):
        label = labels[i]
        table = htmltables[i]
        colrow = table.find_all('tr')[0]
        colnames = colrow.text.strip().split('\n')
        rows = table.find_all('tr')[1:]
        tabledata = []
        for row in rows:
            rowdata = row.text.strip().split('\n')
            if len(colnames) == len(rowdata):
                rowdict = {colnames[i]: rowdata[i]
                    for i in range(len(colnames))}
                tabledata.append(rowdict)
            else:
                if label not in lost.keys(): lost[label] = [rowdata]
                else: lost[label].append(rowdata)
        if not any(tabledata):
            logger.info(f'no records identified for {label}')
            continue
        df = pd.DataFrame(tabledata)
        df['report_batch'] = label
        dfs.append(df)
    assert len(dfs) > 30, f"There should be more than \
    30 tables (>2.5 years) worth of data extracted, \
    found {len(dfs)} tables after processing."
    out = pd.concat(dfs)
    return out, lost


def byany(htmltables):
    if not any(htmltables): return None
    data = []
    lost = []
    for table in htmltables:
        colrow = table.find_all('tr')[0]
        colnames = colrow.text.strip().split('\n')
        rows = table.find_all('tr')[1:]
        for row in rows:
            rowdata = row.text.strip().split('\n')
            if len(colnames) == len(rowdata):
                rowdict = {colnames[i]: rowdata[i]
                    for i in range(len(colnames))}
                data.append(rowdict)
            else: lost.append(rowdata)
    if not any(data): return None
    out = pd.DataFrame(data)
    assert len(data) == out.shape[0], f"\
    Expecting the same number of cows collected as in formatted dataframe; \
    found {len(data)} collected and {out.shape[0]} in df"
    return out, lost
# }}}

# --- main --- {{{
if __name__ == '__main__':
    args = getargs()
    setuplogging("output/format.log")

    logger.info('setting up html data')
    html = readhtml(fname=args.input)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    headers = [h2.text for h2 in soup.find_all('h2')
        if any(re.findall('202[0-9]{1}', h2.text))]
    tables = soup.find_all('table')

    logger.info('begin re-structuring table data')
    if len(headers) == len(tables):
        data = {header: [] for header in headers}
        df, lost = byheader(labels=headers, htmltables=tables)
    else:
        logger.info(f"found {len(headers)} headers and {len(tables)
        } tables in the soup; expecting same count")
        logger.info('first header:', headers[0])
        logger.info('first row:', tables[0].find_all('tr')[1])
        logger.info('\nlast header:', headers[-1])
        logger.info('last row:', tables[-1].find_all('tr')[-1])
        df, lost = byany(htmltables=tables)

    logger.info('standardizing column names')
    df.rename(columns={c: c.lower().replace(' ', '_')
        for c in df.columns}, inplace=True)

    logger.info('writing output')
    df.to_parquet(args.output)
    writeyaml(yamlfile=args.lost, data=lost)

    logger.info('done')
# }}}

# done.
