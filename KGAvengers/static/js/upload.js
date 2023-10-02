document.addEventListener("DOMContentLoaded", function() {
  const uploadForm = document.getElementById("upload-form");
  const resultDiv = document.getElementById("result");

  uploadForm.addEventListener("submit", function(e) {
      e.preventDefault();

      const formData = new FormData(uploadForm);

      fetch("/feed/upload_image/", {
          method: "POST",
          body: formData,
      })
      .then(response => response.json())
      .then(data => {
          if (data.success) {
              resultDiv.innerHTML = `<p>Image uploaded and converted successfully.</p>`;
          } else {
              resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
          }
      })
      .catch(error => {
          console.error("Error:", error);
          resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
      });
  });
});
