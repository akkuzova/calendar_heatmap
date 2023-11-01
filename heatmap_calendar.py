from calendar import HTMLCalendar
from datetime import datetime
from xml.dom import minidom


class HeatMapCalendar(HTMLCalendar):
    current_month = 0
    current_year = 0
    legend = {0: 'light-yellow', 10: 'yellow', 100: 'orange', 1000: 'red'}
    calendar_data = {}

    def get_heatmap(self, theyear, calendar_data, width=3, css='calendar.css', encoding=None) -> str:
        self.calendar_data = calendar_data
        self.current_year = theyear
        html_row = HTMLCalendar.formatyearpage(self, theyear, width, css, encoding)
        html_dom = minidom.parseString(html_row)
        body = html_dom.getElementsByTagName('body').item(0)
        body.insertBefore(self._build_legend(), body.childNodes[0])
        style_tag = self._get_style_tag()
        head_tag = html_dom.getElementsByTagName('head').item(0)
        link_tag = head_tag.getElementsByTagName('link').item(0)
        head_tag.removeChild(link_tag)
        head_tag.appendChild(style_tag)
        return html_dom.toprettyxml()

    def _build_legend(self):
        doc = minidom.Document()
        legend = doc.createElement('tr')
        legend_name = doc.createElement('td')
        legend_text = doc.createTextNode('legend')
        legend_name.appendChild(legend_text)
        legend_name.setAttribute('class', 'legend')
        legend.appendChild(legend_name)
        for threshold, color in self.legend.items():
            elem = doc.createElement('td')
            elem.setAttribute('class', f'legend {color}')
            text = doc.createTextNode(f'> {threshold}')
            elem.appendChild(text)
            legend.appendChild(elem)

        table = doc.createElement('table')
        table.appendChild(legend)
        table.setAttribute('class', 'legend')

        return table

    def _pick_color(self, number):
        l_keys = sorted(self.legend.keys(), reverse=True)
        for threshold in l_keys:
            if number > threshold:
                return self.legend[threshold]
        return ''

    def _get_style_tag(self):
        doc = minidom.Document()
        style = doc.createElement('style')
        style_text = doc.createTextNode(open('heatmap.css').read().replace('\n', ''))
        style.appendChild(style_text)

        return style

    # override methods
    def formatday(self, day, weekday):
        if day == 0:
            # day outside month
            return '<td class="%s">&nbsp;</td>' % self.cssclass_noday
        else:
            current_date = datetime(self.current_year, self.current_month, day).strftime("%Y-%m-%d")

            number = 0 if current_date not in self.calendar_data.keys() else self.calendar_data[current_date]

            tclass = 'td-day ' + self._pick_color(number)
            return '<td class="%s">%d<span class="tooltip">%d</span></td>' % (tclass, day, number)

    def formatmonth(self, theyear, themonth, withyear=False):
        self.current_month = themonth
        return HTMLCalendar.formatmonth(self, theyear, themonth, withyear)
