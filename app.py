from flask import Flask, request, render_template, jsonify, send_file
import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import time
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

RESULTS_URL = "https://egovernance.unom.ac.in/results/ugresultpage.asp"


def fetch_results(regno, dob):
    session = requests.Session()
    payload = {"regno": regno, "pwd": dob, "submit": "Get Result"}
    response = session.post(RESULTS_URL, data=payload)

    if response.status_code != 200:
        return None, "Error fetching results"

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="bordered")
    if not table:
        return None, "Invalid credentials or no results found"

    # ------------------------------
    # Extract Basic Details
    # ------------------------------
    page_text = soup.get_text(" ", strip=True)

    try:
        name = page_text.split("Name :")[1].split("Register Number")[0].strip()
        reg_no = page_text.split("Register Number :")[1].split("DOB")[0].strip()
        dob_extracted = page_text.split("DOB :")[1].split("Month & Year")[0].strip()
    except:
        return None, "Parsing basic info failed"

    # ------------------------------
    # Extract Subjects (Row by Row)
    # ------------------------------
    rows = table.find_all("tr")
    subject_data = []

    for row in rows:
        cols = [col.get_text(strip=True) for col in row.find_all("td")]

        # Expecting at least 5 columns
        if len(cols) >= 5:

            subject_code = cols[0].strip()

            # Skip headers
            if subject_code.lower() in ["subject code", "code"]:
                continue

            ue = cols[1].strip()
            ia = cols[2].strip()
            total = cols[3].strip()
            result = cols[4].strip()

            # Basic validation (subject codes can vary)
            if len(subject_code) >= 4 and any(c.isdigit() for c in subject_code):
                subject_data.append({
                    "Subject Code": subject_code,
                    "UE": ue,
                    "IA": ia,
                    "Total": total,
                    "Result": result
                })

    if not subject_data:
        return None, "No subjects found"

    return {
        "name": name,
        "reg_no": reg_no,
        "dob": dob_extracted,
        "results": subject_data
    }, None
