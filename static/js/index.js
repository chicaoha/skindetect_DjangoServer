__webpack_require__.r(__webpack_exports__);
/* harmony import */
var _node_modules_glightbox_dist_css_glightbox_min_css__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__( /*! ../../node_modules/glightbox/dist/css/glightbox.min.css */ "./node_modules/glightbox/dist/css/glightbox.min.css");
/* harmony import */
var _css_animate_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__( /*! ../css/animate.css */ "./src/css/animate.css");
/* harmony import */
var _css_style_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__( /*! ../css/style.css */ "./src/css/style.css");
/* harmony import */
var alpinejs__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__( /*! alpinejs */ "./node_modules/alpinejs/dist/module.esm.js");
/* harmony import */
var _alpinejs_intersect__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__( /*! @alpinejs/intersect */ "./node_modules/@alpinejs/intersect/dist/module.esm.js");
/* harmony import */
var glightbox__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__( /*! glightbox */ "./node_modules/glightbox/dist/js/glightbox.min.js");
/* harmony import */
var glightbox__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/ __webpack_require__.n(glightbox__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */
var wowjs__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__( /*! wowjs */ "./node_modules/wowjs/dist/wow.js");
/* harmony import */
var wowjs__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/ __webpack_require__.n(wowjs__WEBPACK_IMPORTED_MODULE_6__);







alpinejs__WEBPACK_IMPORTED_MODULE_3__["default"].plugin(_alpinejs_intersect__WEBPACK_IMPORTED_MODULE_4__["default"]);
window.Alpine = alpinejs__WEBPACK_IMPORTED_MODULE_3__["default"];
alpinejs__WEBPACK_IMPORTED_MODULE_3__["default"].start();
window.wow = new (wowjs__WEBPACK_IMPORTED_MODULE_6___default().WOW)({
    live: false
});
window.wow.init({
    offset: 50
}); //========= glightbox

glightbox__WEBPACK_IMPORTED_MODULE_5___default()({
    href: "static/videos/video_hd.mp4'",
    type: "video",
    source: "local",
    width: 900,
    autoplayVideos: true
});


var darkTogglerCheckbox = document.querySelector('#darkToggler');
var html = document.querySelector('html');

var darkModeToggler = function darkModeToggler() {
    darkTogglerCheckbox.checked ? html.classList.add('mj') : html.classList.remove('mj');
};

darkModeToggler();
darkTogglerCheckbox.addEventListener('click', darkModeToggler); // ====== scroll top js

function scrollTo(element) {
    var to = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : 0;
    var duration = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : 500;
    var start = element.scrollTop;
    var change = to - start;
    var increment = 20;
    var currentTime = 0;

    var animateScroll = function animateScroll() {
        currentTime += increment;
        var val = Math.easeInOutQuad(currentTime, start, change, duration);
        element.scrollTop = val;

        if (currentTime < duration) {
            setTimeout(animateScroll, increment);
        }
    };

    animateScroll();
}

Math.easeInOutQuad = function (t, b, c, d) {
    t /= d / 2;
    if (t < 1) return c / 2 * t * t + b;
    t--;
    return -c / 2 * (t * (t - 2) - 1) + b;
};

document.querySelector('.back-to-top').onclick = function () {
    scrollTo(document.documentElement);
};

// Phat installs Datetimepicker
// Import necessary dependencies
import { initTE, Datetimepicker } from 'tailwind-elements';
import 'flowbite-datepicker';
import 'flowbite/dist/datepicker.turbo.js';

// Initialize the components you need
initTE({
    Datetimepicker,
    // Other components...
});

// Your other application logic goes here