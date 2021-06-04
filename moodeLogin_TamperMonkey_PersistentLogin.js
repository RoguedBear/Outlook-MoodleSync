// ==UserScript==
// @name         LMS/Moodle Persistent Login
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  Maintaining a persistent login on lms
// @author       RoguedBear
// @match        https://lms.bennett.edu.in/my/
// @icon         https://lms.bennett.edu.in/theme/image.php/lambda/theme/1609510051/favicon
// @grant        none
// ==/UserScript==

// get current cookie
var cookies = cookieToJSON();
if ("Persistent" in cookies == false) {
    setCookie("MoodleSession", cookies.MoodleSession, 1);
    // set Persistent to 1
    setCookie_Date("Persistent", 1, nextDayDate());
}

// cookie to json
// https://stackoverflow.com/a/30138647
function cookieToJSON() {
    var cookie = document.cookie;
    var output = {};
    cookie.split(/\s*;\s*/).forEach(function (pair) {
        pair = pair.split(/\s*=\s*/);
        var name = decodeURIComponent(pair[0]);
        var value = decodeURIComponent(pair.splice(1).join("="));
        output[name] = value;
    });
    return output;
}

// setCookie
function setCookie(cName, cValue, expDays) {
    let date = new Date();
    date.setTime(date.getTime() + expDays * 24 * 60 * 60 * 1000);
    const expires = "expires=" + date.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
    console.log(cName + "=" + cValue + "; " + expires + "; path=/");
}

function setCookie_Date(cName, cValue, expDate) {
    //   let date = new Date();
    //   date.setTime(date.getTime() + expDays * 24 * 60 * 60 * 1000);
    const expires = "expires=" + expDate.toUTCString();
    document.cookie = cName + "=" + cValue + "; " + expires + "; path=/";
    console.log(cName + "=" + cValue + "; " + expires + "; path=/");
}
// getting next day midnight date
function nextDayDate() {
    var tomorrow = new Date();
    var today = new Date();
    tomorrow.setDate(today.getDate() + 1);
    tomorrow.setHours(0, 1, 0);
    return tomorrow;
}
