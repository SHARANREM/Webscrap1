from flask import Flask, request, render_template, jsonify, send_file
import requests
import re
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
    
    text = "\n".join(row.get_text(strip=False) for row in table.find_all("tr"))
    
    try:
        name = re.search(r"Name\s*:\s*([A-Z\s]+)", text).group(1).strip()[:-1]
        reg_no = re.search(r"Register Number\s*:\s*(\d+)", text).group(1).strip()
        dob = re.search(r"DOB\s*:\s*([\d/]+)", text).group(1).strip()
        data = re.findall(r'(\w{6})\s*(\d{3})(\d{3})(\d{3})(\w+)', text)
        df = pd.DataFrame(data, columns=['Subject Code', 'UE', 'IA', 'Total', 'Result'])
        return {"name": name, "reg_no": reg_no, "dob": dob, "results": df.to_dict(orient='records')}, None
    except AttributeError:
        return None, "Parsing error"


@app.route("/fetch_result", methods=["POST"])
def fetch_single():
    regno = request.form.get("regno", "").strip()
    dob = request.form.get("dob", "").strip()

    if not regno or not dob:
        return jsonify({"error": "Both Register Number and DOB are required."}), 400

    result, error = fetch_results(regno, dob)
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(result)


@app.route("/bulk_upload", methods=["POST"])
def bulk_upload():
    file = request.files["file"]
    if not file:
        return jsonify({"error": "No file uploaded"}), 400
    
    df = pd.read_csv(file) if file.filename.endswith(".csv") else pd.read_excel(file)
    results = []
    all_subjects = set()
    student_data = []
    
    for _, row in df.iterrows():
        regno, dob = str(row["Register No"]), row["DOB"]

        if isinstance(dob, str):
            parts = dob.split("/")
            if len(parts) == 3:
                day = parts[0].zfill(2)  
                month = parts[1].zfill(2)  
                year = parts[2]
                dob = f"{day}/{month}/{year}"


        result, error = fetch_results(regno, dob)
        if error:
            student_data.append({"Name": None, "Register No": regno, "DOB": dob, "Error": error})
        else:
            student_entry = {"Name": result["name"], "Register No": result["reg_no"], "DOB": result["dob"]}
            for r in result["results"]:
                subject = r["Subject Code"]
                all_subjects.add(subject)
                student_entry[subject] = f"UE: {r['UE']}, IA: {r['IA']}, Total: {r['Total']}, Result: {r['Result']}"
            student_data.append(student_entry)
        
        time.sleep(1)  
    
    columns = ["Name", "Register No", "DOB"] + sorted(all_subjects)
    output_df = pd.DataFrame(student_data, columns=columns)
    
    output_file = "bulk_results.xlsx"
    output_df.to_excel(output_file, index=False)
    
    return send_file(output_file, as_attachment=True)


@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)