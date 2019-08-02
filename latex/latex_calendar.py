#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
latex_calendar.py

From: http://www.gov.mb.ca/ctt/invest/busfacts/workforce/stat_hols.html
on: 2009-May-29

There are eight general holidays throughout the year:
* New Year's Day, January 1
* Louis Riel Day (3rd Monday in February)
* Good Friday
* Victoria Day, the Monday preceding May 25
* Canada Day, July 1
* Labour Day, first Monday in September
* Thanksgiving Day, second Monday in October
* Christmas Day, December 25

Individual employers may grant additional days and collective agreements may include additional days off.

Note: Remembrance Day (November 11) is not a General Holiday under Manitoba labour legislation, but requires compulsory closing of all businesses, with some specified exceptions.

Source: Manitoba Labour Employment Standards Branch

TODO: convert this to dateutil, which makes all the calendar computations easier.
"""
#######################
from __future__ import print_function, unicode_literals

import calendar
import datetime
import sys

#######################



def calc_easter(year):
    """returns the date of Easter Sunday of the given yyyy year"""
    # Source: http://www.daniweb.com/code/snippet485.html#
    # Retreived: 2009-May-29
    y = year
    # golden year - 1
    g = y % 19
    # offset
    e = 0
    # century
    c = y//100
    # h is (23 - Epact) mod 30
    h = (c-c//4-(8*c+13)//25+19*g+15)%30
    # number of days from March 21 to Paschal Full Moon
    i = h-(h//28)*(1-(h//28)*(29//(h+1))*((21-g)//11))
    # weekday for Paschal Full Moon (0=Sunday)
    j = (y+y//4+i+2-c+c//4)%7
    # number of days from March 21 to Sunday on or before Paschal Full Moon
    # p can be from -6 to 28
    p = i-j+e
    d = 1+(p+27+(p+6)//40)%31
    m = 3+(p+26)//30
    return datetime.date(y,m,d)


def grayed_out(s, dark=50):
    """
    dark is in the interval (0,100); where 0 = white and 100 = black.
    """
    return '{\\color{black!%d}%s}' % (dark, s)


(MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY, ) = range(7)
#SUNDAY = -1 # fix for N.American weeks starting on Sunday.


def is_nth_day(d, n, weekday):
    """
    Note: The one-liner "clever" approach is buggy.
    """
    #return (d.weekday() == (weekday % 7) ) and ( (n-1)*7+weekday <= d.day < n*7+weekday+1 )
    if d.weekday() != weekday:
        return False
    # rewind to the first of the month
    copy_d = datetime.date(d.year, d.month, 1)
    # advance to the first given weekday of the month
    while copy_d.weekday() != weekday:
        copy_d += datetime.timedelta(days=1)
    # advance by weeks until the n-th occurance
    count = 1
    while count < n:
        copy_d += datetime.timedelta(days=7)
        count += 1
    # are they the same?
    return d == copy_d



def is_holiday(d):
    """
    if the date object d is holiday, return a description, otherwise return None.
    """

    # stat holidays
    if d.month == 1 and d.day == 1:
        return 'New Year\'s Day'
    if d.month == 2 and is_nth_day(d, 3, MONDAY): #d.weekday() == 0 and (1+(3-1)*7+0 <= d.day <= 0+3*7+0):
        # 3rd (3 in *7 factors) monday (final +0)
        return 'Louis Riel Day'
    if d == calc_easter(d.year) - datetime.timedelta(days=2):
        return 'Good Friday'
    if d == calc_easter(d.year):
        return 'Easter Sunday'
    if d.month == 5 and d.weekday() == 0 and (25-7 <= d.day < 25):
        # monday on or before May 24
        return 'Victoria Day'
    if d.month == 7 and d.day == 1:
        return 'Canada Day'
    if d.month == 9 and is_nth_day(d, 1, MONDAY): #d.weekday() == 0 and (1+(1-1)*7+0 <= d.day <= 0+1*7+0):
        # 1st (1 in *7 factors) monday (final +0)
        return 'Labour Day'
    if d.month == 10 and is_nth_day(d, 2, MONDAY): #d.weekday() == 0 and (1+(2-1)*7+0 <= d.day <= 0+2*7+0):
        # 2nd (2 in *7 factors) monday (final +0)
        return 'Thanksgiving Day'
    if d.month == 11 and d.day == 11:
        return 'Rememberance Day'
    if d.month == 12 and d.day == 25:
        return 'Christmas Day'

    # federal holidays
    if d == calc_easter(d.year) + datetime.timedelta(days=1):
        return grayed_out('Easter Monday')
    if d.month == 12 and d.day == 24:
        return grayed_out('Christmas Eve')
    if d.month == 12 and d.day == 26:
        return grayed_out('Boxing Day')
    if d.month == 8 and is_nth_day(d, 1, MONDAY):
        return grayed_out('Terry Fox Day')

    # other holidays
    if d.month == 3 and d.day == 17:
        return grayed_out('St.\ Patrick\'s Day')
    if d.month == 2 and d.day == 14:
        return grayed_out('Valentine\'s Day')
    if d.month == 5 and is_nth_day(d, 2, SUNDAY):
        return grayed_out('Mother\'s Day')
    if d.month == 6 and is_nth_day(d, 3, SUNDAY):
        return grayed_out('Father\'s Day')
    if d.month == 10 and d.day == 31:
        return grayed_out('Halloween')
    if d.month == 12 and d.day == 31:
        return grayed_out('New Year\'s Eve')

    return None



def do_begin_document():
    return '''\\documentclass[12pt]{article}

\\usepackage[letterpaper,landscape,margin=0cm]{geometry}
\\usepackage{tabularx}
\\usepackage{xcolor}
\\usepackage{newcent}
\\usepackage{scalefnt}

\\setlength{\parindent}{0pt}
\\setlength{\columnsep}{0pt}
\\pagestyle{empty}

\\newcommand{\cellformat}[1]{\hspace*{\\fill}\\raisebox{-0.05in}{\Large\\textbf{#1}}\\vspace*{0.95in}}
\\newcommand{\holidayformat}[2]{\hspace*{\\fill}\\raisebox{-0.05in}{\Large\\textbf{#1}}\\vspace*{9.5ex} \\newline\\scalefont{0.8}{#2}}


\\begin{document}
'''


def do_end_document():
    return '\\end{document}\n\n'


def do_begin_month(banner):
    return '''\\vspace*{0.5cm}
    \\begin{center}
        \\textbf{\LARGE %s}

        %%\\vspace*{\\fill}
        \\bigskip

        \\begin{tabularx}{10.0in}{|X|X|X|X|X|X|X|}
        \\hline
''' % banner


def do_end_month():
    return '''\\end{tabularx}
    \\end{center}
    \\vspace*{\\stretch{3}}
    \\newpage
'''


def do_begin_week(first= False, last= False):
    if first:
        return ''
    return '\\hline\n'


def do_end_week(first= False, last= False):
    #result = ''
    #if first:
        #result += '\\hline\n'*2
    result = ' \\\\ \n'
    if first or last:
        result += '\\hline\n'
    return result


def do_day_seperator():
    return ' & '


def do_day(month,d):
    if month == d.month:
        holiday = is_holiday(d)
        if holiday is not None:
            return '\\holidayformat{%d}{%s}' % (d.day, holiday)
        return '\\cellformat{%d}' % d.day
    return '\\cellformat{%s}' % grayed_out(d.day, 25)


def do_dayname(s):  # like do_day, but for the names
    return '\\multicolumn{1}{|c|}{\\textbf{%s}}' % s


def do_day_names(firstday):
    # Jan 1, 2001 was a Monday
    format = '%A'   # a = 3 letter abbrev; A = fullname
    names = [ datetime.date(2001,1,1+i + firstday).strftime(format) for i in range(7) ]

    result = do_begin_week(first=True)
    result += do_day_seperator().join([do_dayname(n) for n in names])
    result += do_end_week(first=True)
    return result


def do_month(year, month):
    # return a "page" of latex for this year / month
    d = datetime.date(year, month, 1)
    month_banner = d.strftime('%B %Y')
    result = do_begin_month(month_banner)
    result += do_day_names(calendar.SUNDAY)
    monthdays = calendar.Calendar(calendar.SUNDAY).monthdatescalendar(year, month)
    for week in monthdays:
        last = False
        if week == monthdays[-1]:
            last = True
        result += do_begin_week(last=last)
        result += do_day_seperator().join([do_day(month,day) for day in week])
        result += do_end_week(last=last)
    result += do_end_month()

    return result





def main(years=None, months=None):
    if isinstance(years, int):
        years = [years,]
    if isinstance(months, int):
        months = [months,]
    today = datetime.date.today()
    if months is None:
        if years is None:
            months = range(today.month, 13)
        else:
            months = range(1, 13)
    if years is None:
        years = [today.year,]
    result = do_begin_document()
    for year in years:
        for month in months:
            result += do_month(year, month)
    result += do_end_document()
    return result


if __name__ == '__main__':
    if not sys.argv[1:]:
        print(main(datetime.date.today().year))
    else:
        for arg in sys.argv[1:]:
            year = int(arg)
            print(main(year))
