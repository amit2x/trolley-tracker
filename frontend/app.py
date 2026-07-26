# Updated Streamlit dashboard for single-history-table architecture
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
from streamlit_autorefresh import st_autorefresh

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from shared.auth import verify_password
from shared.db import get_connection

st.set_page_config(page_title="Trolley Tracker", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False
    st.session_state.role=None
    st.session_state.user_data=None

def get_conn():
    # get_connection() unlocks the encrypted trolley.db with
    # DB_ENCRYPTION_KEY before returning — see shared/db.py
    return get_connection()

def get_current_trolleys():
    conn=get_conn()
    query="""
    SELECT t1.*
    FROM trolley_tracking t1
    JOIN (
        SELECT trolley_id, MAX(timestamp) latest_time
        FROM trolley_tracking
        GROUP BY trolley_id
    ) t2
      ON t1.trolley_id=t2.trolley_id
     AND t1.timestamp=t2.latest_time
    ORDER BY t1.zone,t1.trolley_id;
    """
    df=pd.read_sql(query,conn)
    conn.close()
    if df.empty:
        return df
    df["timestamp"]=pd.to_datetime(df["timestamp"])
    now=datetime.now()
    df["status"]=df.apply(lambda r:"OFFLINE" if now-r["timestamp"]>timedelta(minutes=5) else r["status"],axis=1)
    return df

def login_page():
    st.title("Airport Trolley Tracker — Login")
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Staff Login")
        u=st.text_input("Username",key="au")
        p=st.text_input("Password",type="password",key="ap")
        if st.button("Login as Staff"):
            conn=get_conn();cur=conn.cursor()
            cur.execute("SELECT password,role FROM users WHERE username=?",(u,))
            r=cur.fetchone();conn.close()
            if r and verify_password(p, r[0]):
                st.session_state.logged_in=True
                st.session_state.role=r[1]
                st.session_state.user_data={"username":u}
                st.rerun()
            else: st.error("Invalid credentials")
    with c2:
        st.subheader("Passenger Login")
        u=st.text_input("Username",key="pu")
        pnr=st.text_input("PNR")
        if st.button("Login as Passenger"):
            conn=get_conn();cur=conn.cursor()
            cur.execute("SELECT name,flight_number,scheduled_time,gate FROM passengers WHERE username=? AND pnr=?",(u,pnr))
            r=cur.fetchone();conn.close()
            if r:
                st.session_state.logged_in=True
                st.session_state.role="passenger"
                st.session_state.user_data={"name":r[0],"flight_number":r[1],"scheduled_time":r[2],"gate":r[3]}
                st.rerun()
            else: st.error("Invalid credentials")

def render_autorefresh_controls(key_prefix: str):
    """
    Non-blocking auto-refresh control, shared by both dashboards.

    Unlike Project 0's `time.sleep(60); st.rerun()` — which freezes the
    entire app for the full interval, so no button click or filter change
    registers until the sleep finishes — st_autorefresh() runs a small
    client-side JS timer that triggers a rerun on its own schedule without
    blocking the Python thread. The page stays fully interactive the
    whole time; the person can still click Refresh, change the zone
    filter, or log out at any moment.
    """
    c1, c2 = st.columns([1, 3])
    with c1:
        auto_on = st.toggle("Auto-refresh", value=True, key=f"{key_prefix}_auto_on")
    with c2:
        interval = st.selectbox(
            "Every",
            options=[10, 30, 60, 120],
            format_func=lambda s: f"{s} seconds",
            index=1,
            key=f"{key_prefix}_interval",
            disabled=not auto_on,
        )
    if auto_on:
        st_autorefresh(interval=interval * 1000, key=f"{key_prefix}_autorefresh_tick")

def admin_dashboard():
    st.title("Staff Dashboard")
    st.write(f"Logged in as **{st.session_state.user_data['username']}** ({st.session_state.role})")
    render_autorefresh_controls("admin")
    c1,c2=st.columns(2)
    with c1:
        if st.button("Refresh"): st.rerun()
    with c2:
        if st.button("Logout"):
            st.session_state.logged_in=False; st.rerun()
    df=get_current_trolleys()
    if df.empty:
        st.info("No trolley data.")
        return
    zones=["All Zones"]+sorted(df.zone.unique().tolist())
    z=st.selectbox("Filter by Zone",zones)
    if z!="All Zones":
        df=df[df.zone==z]
    m1,m2,m3,m4=st.columns(4)
    m1.metric("Total",len(df))
    m2.metric("Active",(df.status=="ACTIVE").sum())
    m3.metric("Weak",(df.status=="WEAK_SIGNAL").sum())
    m4.metric("Offline",(df.status=="OFFLINE").sum())
    st.dataframe(df,use_container_width=True)
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

def passenger_dashboard():
    d=st.session_state.user_data
    st.title("Passenger Portal")
    st.write(f"Welcome **{d['name']}**")
    render_autorefresh_controls("passenger")
    c1,c2,c3=st.columns(3)
    c1.metric("Flight",d["flight_number"]);c2.metric("Time",d["scheduled_time"]);c3.metric("Gate",d["gate"])
    if st.button("Logout"):
        st.session_state.logged_in=False;st.rerun()
    if st.button("Refresh"):
        st.rerun()
    df=get_current_trolleys()
    if df.empty:
        st.info("No trolley data.");return
    zone=st.selectbox("Select your Zone",sorted(df.zone.unique().tolist()))
    avail=df[(df.zone==zone)&(df.status=="ACTIVE")]
    if avail.empty:
        st.warning("No active trolleys available.")
    else:
        st.dataframe(avail[["trolley_id","zone","status","timestamp"]],use_container_width=True)
    st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

if not st.session_state.logged_in:
    login_page()
elif st.session_state.role=="passenger":
    passenger_dashboard()
else:
    admin_dashboard()