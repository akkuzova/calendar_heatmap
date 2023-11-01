from calendar import HTMLCalendar
from datetime import datetime


def pick_color(number):
    if number > 1000:
        return 'red'
    elif number > 100:
        return 'orange'
    elif number > 10:
        return 'yellow'
    elif number > 0:
        return 'light-yellow'
    else:
        return ''


class HeatMapCalendar(HTMLCalendar):
    current_month = 0
    current_year = 2022
    calendar_data = {}

    def get_heatmap(self, theyear, calendar_data, width=3, css='calendar.css', encoding=None) -> bytes:
        self.calendar_data = calendar_data
        self.current_year = theyear
        return HTMLCalendar.formatyearpage(self, theyear, width, css, encoding)

    # override methods
    def formatday(self, day, weekday):
        if day == 0:
            # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            current_date = datetime(self.current_year, self.current_month, day).strftime("%Y-%m-%d")
            print(current_date)

            number = 0 if current_date not in self.calendar_data.keys() else self.calendar_data[current_date]

            tclass = 'td-day ' + pick_color(number)
            return '<td class="%s">%d<span class="tooltip">%d</span></td>' % (tclass, day, number)

    def formatmonth(self, theyear, themonth, withyear=False):
        self.current_month = themonth
        return HTMLCalendar.formatmonth(self, theyear, themonth, withyear)
