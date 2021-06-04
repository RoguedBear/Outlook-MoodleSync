// ==UserScript==
// @name         Lms login w/ calendar workaround
// @namespace    http://tampermonkey.net/
// @version      0.1.2
// @description  try to take over the world!
// @author       You
// @match        https://lms.bennett.edu.in/login/index.php
// @icon         https://lms.bennett.edu.in/theme/image.php/lambda/theme/1609510051/favicon
// @grant        none
// ==/UserScript==
let cookieBar = `<div class="form-label">
                        <label for="cookie">or Cookie 😉</label>
                    </div>
                 <div class="form-input">
                        <input type="password" name="cookie" id="cookie" size="15" value="" onchange="">
                    </div>`(function () {
    "use strict";

    var sessionId = prompt("Enter cookie from file");
    if (sessionId != "" && sessionId != null) {
        setCookie("MoodleSession", sessionId, 1);

        window.location = "https://lms.bennett.edu.in/my";
    }
})();

function setCookie(cName, cValue, expDays) {
    let date = new Date();
    date.setTime(date.getTime() + expDays * 24 * 60 * 60 * 1000);
    const expires = "expires=" + date.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
    console.log(cName + "=" + cValue + "; " + expires + "; path=/");
}
