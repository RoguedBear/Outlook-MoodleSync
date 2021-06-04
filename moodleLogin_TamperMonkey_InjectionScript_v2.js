// ==UserScript==
// @name         Lms login w/ calendar workaround v2
// @namespace    http://tampermonkey.net/
// @version      2.0
// @description  try to take over the world!
// @author       You
// @match        https://lms.bennett.edu.in/login/index.php
// @icon         https://lms.bennett.edu.in/theme/image.php/lambda/theme/1609510051/favicon
// @grant        none
// ==/UserScript==

(function () {
    "use strict";

    // first inject html
    let inject = document.createElement("div");
    let cookieBar = `<div class="clearer"><!-- --></div>
                    <div class="form-label">
                        <label for="cookie">or Cookie 😉</label>
                    </div>
                    <div class="form-input">
                        <input type="password" name="cookie" id="cookie" size="15" value="" onchange="updateCookie()">
                    </div>`;
    inject.innerHTML = cookieBar;
    document.querySelector(".loginform").innerHTML += cookieBar;

    var script = document.createElement("script");
    script.setAttribute("type", "application/javascript");
    script.textContent =
        updateCookie.toString() + "; " + setCookie.toString() + ";";
    document.body.appendChild(script); // run the script
})();

function updateCookie() {
    var sessionId = document.getElementById("cookie").value;
    setCookie("MoodleSession", sessionId, 1);
    setCookie("Persistent", 1, 1);
    window.location = "https://lms.bennett.edu.in/my";
}

function setCookie(cName, cValue, expDays) {
    let date = new Date();
    date.setTime(date.getTime() + expDays * 24 * 60 * 60 * 1000);
    const expires = "expires=" + date.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
    console.log(cName + "=" + cValue + "; " + expires + "; path=/");
}
