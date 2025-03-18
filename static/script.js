// Single Result Submission
document.getElementById("singleResultForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const dobInput = document.getElementById("dob").value;  // "2005-10-03"
  const formattedDOB = dobInput.split("-").reverse().join("/");  // Converts to "03/10/2005"

  const formData = new FormData();
  formData.append("regno", document.getElementById("regno").value.trim());
  formData.append("dob", formattedDOB);  // Correct format for your Flask app

  const response = await fetch("/fetch_result", {
      method: "POST",
      body: formData
  });

  const resultDisplay = document.createElement("div");
  if (response.ok) {
      const data = await response.json();
      resultDisplay.innerHTML = "";
      resultDisplay.innerHTML = `
          <div class='alert alert-success'>
              <strong>Name:</strong> ${data.name}<br>
              <strong>Register No:</strong> ${data.reg_no}<br>
              <strong>DOB:</strong> ${data.dob}<br>
              <strong>Results:</strong> ${data.results.map(r => `
                  <br>
                  <strong>${r["Subject Code"]}:</strong> ${r.Total} (${r.Result})
              `).join("")}
          </div>`;
  } else {
      const errorData = await response.json();
      resultDisplay.innerHTML = `<div class='alert alert-danger'>${errorData.error}</div>`;
  }

  document.querySelector(".container").appendChild(resultDisplay);
});



// Bulk Upload Submission
document
  .getElementById("bulkResultForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    const fileInput = document.getElementById("fileUpload");
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch("/bulk_upload", {
      method: "POST",
      body: formData,
    });

    const bulkResultMessage = document.createElement("div");
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "bulk_results.xlsx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      bulkResultMessage.innerHTML ="";
      bulkResultMessage.innerHTML = `<div class='alert alert-success'>Bulk results downloaded successfully!</div>`;
    } else {
      const errorData = await response.json();
      bulkResultMessage.innerHTML = "";  
      bulkResultMessage.innerHTML = `<div class='alert alert-danger'>${errorData.error}</div>`;
    }

    document.querySelector(".container").appendChild(bulkResultMessage);
  });
