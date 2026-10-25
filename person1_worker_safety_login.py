import streamlit as st
import pandas as pd
import json
from pathlib import Path


# -----------------------------------
# FILE LOCATIONS
# -----------------------------------

BASE = Path(__file__).resolve().parent

USERS_FILE = BASE / "users.json"

WORKERS_FILE = BASE / "workers.csv"


# -----------------------------------
# PAGE SETTINGS
# -----------------------------------

st.set_page_config(
    page_title="Khwezi Mining - Worker Safety",
    page_icon="\u26CF",
    layout="wide"
)


# -----------------------------------
# USER ROLE ACCESS
# -----------------------------------

ROLE_ACCESS = {
    "Administrator": True,
    "Safety Officer": True,
    "Mining Engineer": True,
    "Maintenance Engineer": False,
    "Manager": True,
}


# -----------------------------------
# LOAD USERS
# -----------------------------------

def load_users():

    with open(
        USERS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# -----------------------------------
# LOAD WORKERS
# -----------------------------------

def load_workers():

    return pd.read_csv(
        WORKERS_FILE
    )


# -----------------------------------
# SAVE WORKERS
# -----------------------------------

def save_workers(df):

    df.to_csv(
        WORKERS_FILE,
        index=False
    )


# -----------------------------------
# WORKER RISK CLASSIFICATION
# -----------------------------------

def classify_worker_risk(
    ppe,
    training,
    fatigue,
    near_misses,
    previous_incidents
):

    score = 0

    if ppe == "No":

        score += 4


    if training == "No":

        score += 3


    if fatigue == 4:

        score += 2

    elif fatigue == 5:

        score += 4


    if near_misses >= 2:

        score += 2

    elif near_misses == 1:

        score += 1


    if previous_incidents >= 1:

        score += 1


    if score >= 8:

        return "High"

    elif score >= 4:

        return "Medium"

    else:

        return "Low"


# -----------------------------------
# GENERATE WORKER WARNINGS
# -----------------------------------

def generate_worker_warnings(row):

    warnings = []


    if row["PPECompliance"] == "No":

        warnings.append(
            "HIGH: PPE non-compliance detected."
        )


    if row["SafetyTraining"] == "No":

        warnings.append(
            "WARNING: Safety training is incomplete."
        )


    if int(row["FatigueLevel"]) == 5:

        warnings.append(
            "CRITICAL: Very high fatigue level detected."
        )

    elif int(row["FatigueLevel"]) == 4:

        warnings.append(
            "WARNING: High fatigue level detected."
        )


    if int(row["NearMisses"]) >= 2:

        warnings.append(
            "WARNING: Multiple near misses recorded."
        )

    elif int(row["NearMisses"]) == 1:

        warnings.append(
            "NOTICE: A near miss has been recorded."
        )


    if int(row["SafetyObservations"]) >= 3:

        warnings.append(
            "NOTICE: Several safety observations require review."
        )


    if int(row["PreviousIncidents"]) >= 2:

        warnings.append(
            "WARNING: Worker has multiple previous incidents."
        )


    if not warnings:

        warnings.append(
            "NORMAL: No immediate worker safety warning identified."
        )


    return warnings


# -----------------------------------
# LOGIN PAGE
# -----------------------------------

def login_page():

    st.title(
        "Khwezi Mining"
    )

    st.subheader(
        "Worker Health and Safety Monitoring"
    )

    st.write(
        "Login to access the application."
    )


    with st.form(
        "login_form"
    ):

        username = st.text_input(
            "Username"
        )

        password = st.text_input(
            "Password",
            type="password"
        )

        login_button = st.form_submit_button(
            "Login"
        )


    if login_button:

        users = load_users()


        if (
            username in users
            and users[username]["password"] == password
        ):

            st.session_state.logged_in = True

            st.session_state.username = username

            st.session_state.role = (
                users[username]["role"]
            )

            st.rerun()


        else:

            st.error(
                "Invalid username or password."
            )


# -----------------------------------
# LOGIN SESSION
# -----------------------------------

if "logged_in" not in st.session_state:

    st.session_state.logged_in = False


if not st.session_state.logged_in:

    login_page()

    st.stop()


# -----------------------------------
# USER ROLE
# -----------------------------------

role = st.session_state.role


# -----------------------------------
# SIDEBAR
# -----------------------------------

with st.sidebar:

    st.header(
        "User Information"
    )

    st.write(
        f"Username: **{st.session_state.username}**"
    )

    st.write(
        f"Role: **{role}**"
    )


    if st.button(
        "Logout"
    ):

        st.session_state.clear()

        st.rerun()


# -----------------------------------
# MAIN PAGE
# -----------------------------------

st.title(
    "Worker Health and Safety Monitoring"
)


# -----------------------------------
# CHECK USER ACCESS
# -----------------------------------

if not ROLE_ACCESS.get(
    role,
    False
):

    st.error(
        "Access denied. Your role does not have "
        "permission to view worker safety data."
    )

    st.stop()


# -----------------------------------
# LOAD WORKER DATA
# -----------------------------------

workers = load_workers()


# -----------------------------------
# CALCULATE RISK LEVEL
# -----------------------------------

workers["RiskLevel"] = workers.apply(

    lambda row: classify_worker_risk(

        row["PPECompliance"],

        row["SafetyTraining"],

        int(row["FatigueLevel"]),

        int(row["NearMisses"]),

        int(row["PreviousIncidents"])

    ),

    axis=1
)


# -----------------------------------
# CALCULATE SAFETY INFORMATION
# -----------------------------------

total_workers = len(
    workers
)


ppe_compliant = (
    workers["PPECompliance"] == "Yes"
).sum()


if total_workers > 0:

    ppe_percentage = (
        ppe_compliant
        / total_workers
        * 100
    )

else:

    ppe_percentage = 0


high_fatigue = (
    workers["FatigueLevel"] >= 4
).sum()


training_incomplete = (
    workers["SafetyTraining"] == "No"
).sum()


total_near_misses = (
    workers["NearMisses"].sum()
)


# -----------------------------------
# DISPLAY SAFETY METRICS
# -----------------------------------

c1, c2, c3, c4, c5 = st.columns(5)


c1.metric(
    "Total Workers",
    total_workers
)


c2.metric(
    "PPE Compliance",
    f"{ppe_percentage:.1f}%"
)


c3.metric(
    "High Fatigue",
    int(high_fatigue)
)


c4.metric(
    "Training Incomplete",
    int(training_incomplete)
)


c5.metric(
    "Near Misses",
    int(total_near_misses)
)


# -----------------------------------
# DISPLAY WORKER TABLE
# -----------------------------------

st.subheader(
    "Worker Safety Records"
)


st.dataframe(
    workers,
    use_container_width=True,
    hide_index=True
)


# -----------------------------------
# CHECK INDIVIDUAL WORKER
# -----------------------------------

st.subheader(
    "Check Individual Worker"
)


selected_worker = st.selectbox(
    "Select Worker ID",
    workers["WorkerID"].tolist()
)


selected_row = workers[
    workers["WorkerID"] == selected_worker
].iloc[0]


st.write(
    f"Department: **{selected_row['Department']}**"
)


st.write(
    f"Job Role: **{selected_row['JobRole']}**"
)


st.write(
    f"Shift: **{selected_row['Shift']}**"
)


st.write(
    f"Risk Level: **{selected_row['RiskLevel']}**"
)


# -----------------------------------
# DISPLAY WARNINGS
# -----------------------------------

for warning in generate_worker_warnings(
    selected_row
):

    if (
        warning.startswith("CRITICAL")
        or warning.startswith("HIGH")
    ):

        st.error(
            warning
        )


    elif warning.startswith(
        "WARNING"
    ):

        st.warning(
            warning
        )


    elif warning.startswith(
        "NOTICE"
    ):

        st.info(
            warning
        )


    else:

        st.success(
            warning
        )


# -----------------------------------
# ADD NEW WORKER
# -----------------------------------

st.subheader(
    "Add Worker Safety Record"
)


with st.form(
    "add_worker_form"
):

    col1, col2, col3 = st.columns(3)


    worker_id = col1.text_input(
        "Worker ID"
    )


    department = col2.selectbox(
        "Department",
        [
            "Mining",
            "Engineering",
            "Safety",
            "Plant",
            "Other"
        ]
    )


    job_role = col3.text_input(
        "Job Role"
    )


    col1, col2, col3 = st.columns(3)


    shift = col1.selectbox(
        "Shift",
        [
            "Day",
            "Night"
        ]
    )


    ppe = col2.selectbox(
        "PPE Compliant?",
        [
            "Yes",
            "No"
        ]
    )


    training = col3.selectbox(
        "Safety Training Complete?",
        [
            "Yes",
            "No"
        ]
    )


    col1, col2, col3 = st.columns(3)


    fatigue = col1.slider(
        "Fatigue Level",
        1,
        5,
        2
    )


    observations = col2.number_input(
        "Safety Observations",
        min_value=0,
        step=1
    )


    near_misses = col3.number_input(
        "Near Misses",
        min_value=0,
        step=1
    )


    previous_incidents = st.number_input(
        "Previous Incidents",
        min_value=0,
        step=1
    )


    save_button = st.form_submit_button(
        "Save Worker Record"
    )


# -----------------------------------
# SAVE NEW WORKER
# -----------------------------------

if save_button:


    if worker_id.strip() == "":

        st.error(
            "Worker ID cannot be empty."
        )


    elif worker_id in workers[
        "WorkerID"
    ].astype(str).values:

        st.error(
            "Worker ID already exists."
        )


    elif job_role.strip() == "":

        st.error(
            "Job role cannot be empty."
        )


    else:

        new_worker = pd.DataFrame(

            [[
                worker_id,
                department,
                job_role,
                shift,
                ppe,
                training,
                fatigue,
                observations,
                near_misses,
                previous_incidents
            ]],

            columns=[
                "WorkerID",
                "Department",
                "JobRole",
                "Shift",
                "PPECompliance",
                "SafetyTraining",
                "FatigueLevel",
                "SafetyObservations",
                "NearMisses",
                "PreviousIncidents"
            ]

        )


        original_workers = load_workers()


        updated_workers = pd.concat(

            [
                original_workers,
                new_worker
            ],

            ignore_index=True

        )


        save_workers(
            updated_workers
        )


        st.success(
            "Worker safety record saved successfully."
        )


        st.rerun()
