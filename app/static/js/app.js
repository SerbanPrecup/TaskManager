// ======= Shared helpers (moved from base.html) =======
function getCSRFToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  return meta ? meta.getAttribute("content") : "";
}

function postJSON(url, data) {
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify(data),
  });
}

// Expose if needed elsewhere
window.getCSRFToken = getCSRFToken;
window.postJSON = postJSON;
