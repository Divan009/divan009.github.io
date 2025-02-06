$(document).ready(function () {

    $(window).scroll(function () {
        if ($(this).scrollTop() > 100) {
            $('.scrollup').fadeIn();
        } else {
            $('.scrollup').fadeOut();
        }
    });

    $('.circle-button').click(function () {
        $("html, body").animate({
            scrollTop: 0
        }, 600);
        return false;
    });

    $('.print-button').click(function () {
        window.print();
        return false;
    });

    // Dark Mode Toggle Button
    const toggleBtn = $('#darkModeToggle');
    const body = $('body');

    // Check localStorage for mode preference
    if (localStorage.getItem("darkMode") === "enabled") {
        enableDarkMode();
    }

    toggleBtn.click(function () {
        if (body.hasClass("dark-mode")) {
            disableDarkMode();
        } else {
            enableDarkMode();
        }
    });

    function enableDarkMode() {
        body.addClass("dark-mode");
        localStorage.setItem("darkMode", "enabled");
        toggleBtn.text("☀️ Light Mode");
    }

    function disableDarkMode() {
        body.removeClass("dark-mode");
        localStorage.setItem("darkMode", "disabled");
        toggleBtn.text("🌙 Dark Mode");
    }
});
