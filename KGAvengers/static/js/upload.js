// KGAvengers/static/js/upload.js
document.addEventListener("DOMContentLoaded", function() {
  const form = document.querySelector("#image-upload-form");
  const imageDisplay = document.querySelector("#image-display");

  form.addEventListener("submit", async function(e) {
      e.preventDefault();
      
      const formData = new FormData(form);
      const response = await fetch("/upload_image/", {
          method: "POST",
          body: formData,
      });

      if (response.ok) {
          const imageURL = await response.text();
          imageDisplay.innerHTML = `<img src="${imageURL}" alt="Uploaded Image">`;
      } else {
          console.error("Image upload failed");
      }
  });
});
