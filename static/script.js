
document.getElementById("singleResultForm").addEventListener("submit", async function(event) {
  event.preventDefault();

  const dobInput = document.getElementById("dob").value;  
  const formattedDOB = dobInput.split("-").reverse().join("/");  

  const formData = new FormData();
  formData.append("regno", document.getElementById("regno").value.trim());
  formData.append("dob", formattedDOB);  

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



document.getElementById("bulkResultForm").addEventListener("submit", async function (event) {
  event.preventDefault();

  const fileInput = document.getElementById("fileUpload");
  const formData = new FormData();
  formData.append("file", fileInput.files[0]);

  const downloadStatus = document.getElementById("download-status");
  downloadStatus.textContent = "Processing... Your download will be started soon";
  

  try {
      const response = await fetch("/bulk_upload", {
          method: "POST",
          body: formData,
      });

      if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.error);
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "bulk_results.xlsx";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);

      setTimeout(() => {
          downloadStatus.textContent="Process Bulk Results";
      }, 2000);
      
      const bulkResultMessage = document.createElement("div");
      bulkResultMessage.innerHTML = `<div class='alert alert-success'>Bulk results downloaded successfully!</div>`;
      document.querySelector(".container").appendChild(bulkResultMessage);

  } catch (error) {
      console.error("Error:", error);
      downloadStatus.textContent = "Process Bulk Results Failed";
      alert("An error occurred: " + error.message);
  }
});
