from heatmap_calendar import HeatMapCalendar
import pandas as pd
import re
import streamlit as st
from datetime import date
import random
import os


def file_upload():
    uploaded_file = st.file_uploader("Choose a csv file to upload", ['csv'])
    if uploaded_file is None:
        return

    return pd.read_csv(uploaded_file)


def group_by_date(df, date_containing_column, number_containing_columns):
    df['_number'] = df[number_containing_columns].sum(axis=1)

    df = df.groupby([date_containing_column]).agg({'_number': sum})

    return df


def save_html(html, filename):
    file = open(filename, 'w')
    file.write(html)


def validate(df, date_column, number_columns):
    for key, row in df.iterrows():
        _date = re.match("\d\d\d\d-\d\d-\d\d", str(row[date_column]))
        if not _date:
            st.error(f'Row {key}, {row} contains wrong date {row[date_column]}')
            return False

        for number_column in number_columns:
            if not str(row[number_column]).isnumeric():
                st.error(f'Row {key}, {row} contains non-numeric value {row[number_column]}')
                return False
    return True


def set_columns(df, default_numbers=None, default_date=0):
    if default_numbers is None:
        default_numbers = [1]
    if len(df.columns) < 2:
        st.error(f'{len(df.columns)} is not enough columns. At least date and number needed')
        return
    date_column = st.selectbox('Choose column that contains date in yyyy-mm-dd format', df.columns, default_date)
    columns = [df.columns[i] for i in default_numbers]
    number_column = st.multiselect('Choose columns that contain values to count', df.columns, columns)

    return date_column, number_column


def get_years(df, date_column):
    years = set(df[date_column].apply(lambda x: int(re.match("\d\d\d\d", x)[0])))
    return sorted(years, reverse=True)


def build_css_in(html):
    css_line = open('heatmap.css').read().replace('\n', '')
    return re.sub('<link.*/>', f'<style>{css_line}</style>', html)


def get_example_df():
    ex_name = 'example_df.csv'
    if os.path.exists(ex_name):
        return pd.read_csv(ex_name)

    start_date = date(1992, 1, 1)
    end_date = date(1993, 12, 31)
    NUMBER_OF_DATES = 300
    date_range = range(start_date.toordinal(), end_date.toordinal())
    random_dates = [date.fromordinal(o) for o in random.sample(date_range, NUMBER_OF_DATES)]
    _dict = {'col_1': {}, 'col_2': {}}

    for _date in random_dates:
        _dict['col_1'][_date.strftime('%Y-%m-%d')] = random.randint(50, 1100)
        _dict['col_2'][_date.strftime('%Y-%m-%d')] = random.randint(0, 60)
    df = pd.DataFrame(_dict)
    df.to_csv(ex_name)

    return df.reset_index()


def main():
    _source = st.radio('Choose source', ['Use example', 'Upload file'], index=0)

    if _source == 'Use example':
        st.session_state.original_df = get_example_df()
        date_containing_column, number_containing_columns = set_columns(st.session_state.original_df, [1, 2], 0)
    else:
        st.session_state.original_df = file_upload()
        date_containing_column, number_containing_columns = set_columns(st.session_state.original_df)

    if st.session_state.original_df is None:
        return

    st.write('Your table:')
    st.dataframe(st.session_state.original_df, width=1000)

    if not validate(st.session_state.original_df, date_containing_column, number_containing_columns):
        return

    by_date_df = group_by_date(st.session_state.original_df, date_containing_column, number_containing_columns)

    st.write('Grouped table:')
    st.dataframe(by_date_df, width=1000)

    year = st.selectbox('Choose Year:', get_years(st.session_state.original_df, date_containing_column))

    year_calendar = HeatMapCalendar()
    html_code = year_calendar.get_heatmap(year, by_date_df.to_dict()['_number']).decode()
    html_code = build_css_in(html_code)

    if st.button(f'Save to {year}_calendar.html'):
        save_html(html_code, f'{year}_calendar.html')
        st.write("Saved")

    st.write('Calendar')
    legend = '<div class=red>>1000</div><div class=orange>>100</div><div class=yellow>>10</div><div class=light-yellow>>0</div>'
    st.markdown(f'<div class=calendar>{legend}{html_code}</div>', unsafe_allow_html=True)


main()
