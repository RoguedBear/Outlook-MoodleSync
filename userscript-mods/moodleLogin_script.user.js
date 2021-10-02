// ==UserScript==
// @name         Lms login w/ calendar workaround
// @namespace    http://tampermonkey.net/
// @version      0.1.2
// @description  try to take over the world!
// @author       RoguedBear
// @match        https://*/login/index.php
// @icon         https://tracker.moodle.org/secure/attachment/68503/Moodle_Circle_M_RGB.png
// @grant        none
// ==/UserScript==

var sessionId = prompt("Enter cookie from file");
if (sessionId != "" && sessionId != null) {
  setCookie("MoodleSession", sessionId, 1);

  window.location = "https://lms.bennett.edu.in/my";
}

function setCookie(cName, cValue, expDays) {
  let date = new Date();
  date.setTime(date.getTime() + expDays * 24 * 60 * 60 * 1000);
  const expires = "expires=" + date.toUTCString();
  document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
  console.log(cName + "=" + cValue + "; " + expires + "; path=/");
}