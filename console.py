import sqlite3
import streamlit as st
from datetime import datetime
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

conn = sqlite3.connect('bp_dbms.db')
c = conn.cursor()

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))
    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    return data


def create_bptable():
    c.execute('CREATE TABLE IF NOT EXISTS bptable(username TEXT, date TEXT, sys REAL,  dia REAL, pulse REAL, bp TEXT)')


def add_bpdata(username, date, sys, dia, pulse, bp):
    c.execute('INSERT INTO bptable(username, date, sys, dia, pulse, bp) VALUES (?, ?, ?, ?, ?, ?)', (username, date, sys, dia, pulse, bp))
    conn.commit()


def convert_df(df):
   return df.to_csv(index=False).encode('utf-8')


def get_table(username):
    query = c.execute('SELECT * FROM bptable')
    cols = [column[0] for column in query.description]
    results = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    results = results[results.username == username]
    return results

st.title('Blood Pressure Monitor')
st.sidebar.title('Authentication: ')
prompt = st.sidebar.selectbox("Options: ", ["Log-in", "Sign-up"])

### Log-in
if prompt == "Log-in":
    st.sidebar.subheader("Log-in Section")
    username = st.sidebar.text_input("Username:")
    password = st.sidebar.text_input("Password:", type='password')
    if st.sidebar.checkbox('Confirm Log-in'):
        create_usertable()
        login = login_user(username, password)
        if login:
            create_bptable()
            st.sidebar.success("Welcome back: {}".format(username))
            add, disp = st.tabs(['Add Data', 'Display Data'])
            with add:
                st.header('Add Blood Pressure Entry')
                current_dateTime = datetime.now()
                st.write('Date and Time', current_dateTime)
                sys = st.number_input('Systolic: ')
                dia = st.number_input('Diastolic: ')
                pulse = st.number_input('Pulse: ')
                bp = f'{sys}/{dia}'
                if (sys != "") & (dia != "") & (pulse != ""):
                    confirm = st.button('Add to Database')
                    if confirm:
                        try:
                            add_bpdata(username, current_dateTime, sys, dia, pulse, bp)
                            st.success('Successfully Added an Entry')
                        except Exception as e:
                            st.error('Recheck Entries')
                            st.write(e)
            with disp:
                try:
                    data = get_table(username)
                    st.write(data)
                    st.download_button(
                        "Download Table",
                        convert_df(data),
                        f"{username}_data.csv",
                        "text/csv",
                        key='download-csv'
                    )
                    st.subheader('Diastolic Trend')
                    fig = px.line(x=data.index, y=data.dia)
                    fig.add_hrect(y0=0, y1=80, line_width=0, fillcolor="green", opacity=0.2)
                    fig.add_hrect(y0=80, y1=89, line_width=0, fillcolor="yellow", opacity=0.2)
                    fig.add_hrect(y0=90, y1=120, line_width=0, fillcolor="orange", opacity=0.2)
                    fig.add_hrect(y0=120, y1=300, line_width=0, fillcolor="red", opacity=0.2)
                    st.plotly_chart(fig)
                    st.subheader('Systolic Trend')
                    fig = px.line(x=data.index, y=data.sys)
                    fig.add_hrect(y0=0, y1=120, line_width=0, fillcolor="green", opacity=0.2)
                    fig.add_hrect(y0=120, y1=129, line_width=0, fillcolor="yellow", opacity=0.2)
                    fig.add_hrect(y0=130, y1=180, line_width=0, fillcolor="orange", opacity=0.2)
                    fig.add_hrect(y0=180, y1=300, line_width=0, fillcolor="red", opacity=0.2)
                    st.plotly_chart(fig)
                except Exception as e:
                    st.error(e)
        else:
            st.sidebar.error('Invalid username/password')
### Sign Up
if prompt == "Sign-up":
    st.sidebar.subheader("Sign-up")
    new_user = st.sidebar.text_input('Username:')
    new_password = st.sidebar.text_input('Password', type='password')
    if st.sidebar.button("Sign-up"):
        create_usertable()
        add_userdata(new_user, new_password)
        st.sidebar.success("You have successfully created a BP Monitoring account!")
        st.sidebar.info('Proceed to Log-in')