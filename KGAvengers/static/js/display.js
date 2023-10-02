window.addEventListener('DOMContentLoaded', (event) => {
  const urlParams = new URLSearchParams(window.location.search);
  const imageId = urlParams.get('image_id');

  fetch('/get_image?image_id=' + imageId)
  .then(response => response.blob())
  .then(images => {
      var objectURL = URL.createObjectURL(images);
      document.querySelector('#displayImage').src = objectURL;
  });
});
