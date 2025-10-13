(function () {
  document.addEventListener("DOMContentLoaded", () => {
    const form =
      document.querySelector('form[action*="auth.register"]') ||
      document.querySelector("form");
    const usernameEl = document.getElementById("username");
    const emailEl = document.getElementById("email");
    const passwordEl = document.getElementById("password");
    const confirmEl = document.getElementById("confirm_password");
    const submitBtn =
      document.getElementById("submitBtn") ||
      document.querySelector('button[type="submit"]');

    const reqLen = document.getElementById("req-length");
    const reqUpper = document.getElementById("req-upper");
    const reqLower = document.getElementById("req-lower");
    const reqDigitSpec = document.getElementById("req-digit-special");
    const reqNoUser = document.getElementById("req-no-username");
    const reqNoEmail = document.getElementById("req-no-email");
    const reqNoSimple = document.getElementById("req-no-simple");

    const csrfInput = document.querySelector('input[name="csrf_token"]');
    const CSRF = csrfInput ? csrfInput.value : null;

    function setMark(li, ok) {
      if (!li) return;
      const text = li.textContent.replace(/^[✅❌]\s*/, "");
      li.textContent = (ok ? "✅ " : "❌ ") + text;
      li.classList.toggle("text-success", ok);
      li.classList.toggle("text-danger", !ok);
    }

    let t;
    function debounce(fn, ms = 200) {
      return (...args) => {
        clearTimeout(t);
        t = setTimeout(() => fn(...args), ms);
      };
    }

    async function validate() {
      const username = (usernameEl?.value || "").trim();
      const email = (emailEl?.value || "").trim();
      const password = passwordEl?.value || "";
      const confirm = confirmEl?.value || "";

      if (!password) {
        submitBtn?.setAttribute("disabled", "disabled");
        submitBtn?.classList.add("disabled");
        setMark(reqLen, false);
        setMark(reqUpper, false);
        setMark(reqLower, false);
        setMark(reqDigitSpec, false);
        setMark(reqNoUser, true);
        setMark(reqNoEmail, true);
        setMark(reqNoSimple, true);
        return;
      }

      const res = await fetch(`${window.location.origin}/password-check`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(CSRF ? { "X-CSRFToken": CSRF } : {}),
        },
        body: JSON.stringify({ username, email, password }),
      });

      let data = {};
      try {
        data = await res.json();
      } catch (_) {}

      setMark(reqLen, !!data.length);
      setMark(reqUpper, !!data.uppercase);
      setMark(reqLower, !!data.lowercase);
      setMark(reqDigitSpec, !!(data.digit || data.special));
      setMark(reqNoUser, data.username_in_password === false);
      setMark(reqNoEmail, data.email_in_password === false);
      setMark(reqNoSimple, data.simple_sequences === false);

      const confirmOK = !confirm || password === confirm;

      const ok = !!data.strong && confirmOK;

      if (ok) {
        submitBtn?.removeAttribute("disabled");
        submitBtn?.classList.remove("disabled");
      } else {
        submitBtn?.setAttribute("disabled", "disabled");
        submitBtn?.classList.add("disabled");
      }
    }

    const run = debounce(validate, 200);

    ["input", "change"].forEach((ev) => {
      usernameEl?.addEventListener(ev, run);
      emailEl?.addEventListener(ev, run);
      passwordEl?.addEventListener(ev, run);
      confirmEl?.addEventListener(ev, run);
    });

    validate();
  });
})();
