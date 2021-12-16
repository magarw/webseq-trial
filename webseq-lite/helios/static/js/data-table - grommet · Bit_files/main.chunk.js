(window["webpackJsonp"] = window["webpackJsonp"] || []).push([["main"],{

/***/ "./config/webpackHotDevClient.js":
/*!***************************************!*\
  !*** ./config/webpackHotDevClient.js ***!
  \***************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

"use strict";
/**
 * Copyright (c) 2015-present, Facebook, Inc.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
 // This alternative WebpackDevServer combines the functionality of:
// https://github.com/webpack/webpack-dev-server/blob/webpack-1/client/index.js
// https://github.com/webpack/webpack/blob/webpack-1/hot/dev-server.js
// It only supports their simplest configuration (hot updates on same server).
// It makes some opinionated choices on top, like adding a syntax error overlay
// that looks similar to our console output. The error overlay is inspired by:
// https://github.com/glenjamin/webpack-hot-middleware

var SockJS = __webpack_require__(/*! sockjs-client */ "./node_modules/sockjs-client/lib/entry.js");

var stripAnsi = __webpack_require__(/*! strip-ansi */ "./node_modules/strip-ansi/index.js");

var url = __webpack_require__(/*! url */ "./node_modules/url/url.js");

var launchEditorEndpoint = __webpack_require__(/*! react-dev-utils/launchEditorEndpoint */ "./node_modules/react-dev-utils/launchEditorEndpoint.js");

var formatWebpackMessages = __webpack_require__(/*! react-dev-utils/formatWebpackMessages */ "./node_modules/react-dev-utils/formatWebpackMessages.js");

var ErrorOverlay = __webpack_require__(/*! react-error-overlay */ "./node_modules/react-error-overlay/lib/index.js");

ErrorOverlay.setEditorHandler(function editorHandler(errorLocation) {
  // Keep this sync with errorOverlayMiddleware.js
  fetch(launchEditorEndpoint + '?fileName=' + window.encodeURIComponent(errorLocation.fileName) + '&lineNumber=' + window.encodeURIComponent(errorLocation.lineNumber || 1) + '&colNumber=' + window.encodeURIComponent(errorLocation.colNumber || 1));
}); // We need to keep track of if there has been a runtime error.
// Essentially, we cannot guarantee application state was not corrupted by the
// runtime error. To prevent confusing behavior, we forcibly reload the entire
// application. This is handled below when we are notified of a compile (code
// change).
// See https://github.com/facebook/create-react-app/issues/3096

var hadRuntimeError = false;
ErrorOverlay.startReportingRuntimeErrors({
  onError: function onError() {
    hadRuntimeError = true;
  },
  filename: '/static/js/bundle.js'
});

if ( true && typeof module.hot.dispose === 'function') {
  module.hot.dispose(function () {
    // TODO: why do we need this?
    ErrorOverlay.stopReportingRuntimeErrors();
  });
} // Connect to WebpackDevServer via a socket.


var connection = new SockJS(url.format({
  protocol: window.location.protocol,
  hostname: window.location.hostname,
  port: window.location.port,
  // Hardcoded in WebpackDevServer
  pathname: '/sockjs-node'
})); // Unlike WebpackDevServer client, we won't try to reconnect
// to avoid spamming the console. Disconnect usually happens
// when developer stops the server.

connection.onclose = function () {
  if (typeof console !== 'undefined' && typeof console.info === 'function') {
    console.info('The development server has disconnected.\nRefresh the page if necessary.');
    sendMessageToRoot('devServerDisconnected', {});
  }
}; // Remember some state related to hot module replacement.


var isFirstCompilation = true;
var mostRecentCompilationHash = null;
var hasCompileErrors = false;

function clearOutdatedErrors() {
  // Clean up outdated compile errors, if any.
  if (typeof console !== 'undefined' && typeof console.clear === 'function') {
    if (hasCompileErrors) {
      console.clear();
    }
  }
} // Successful compilation.


function handleSuccess() {
  clearOutdatedErrors();
  var isHotUpdate = !isFirstCompilation;
  isFirstCompilation = false;
  hasCompileErrors = false;
  sendMessageToRoot('handleWebpackSuccess', {
    isHotUpdate: isHotUpdate,
    isFirstCompilation: isFirstCompilation,
    hasCompileErrors: hasCompileErrors
  }); // Attempt to apply hot updates or reload.

  if (isHotUpdate) {
    tryApplyUpdates(function onHotUpdateSuccess() {
      // Only dismiss it when we're sure it's a hot update.
      // Otherwise it would flicker right before the reload.
      tryDismissErrorOverlay();
    });
  }
} // Compilation with warnings (e.g. ESLint).


function handleWarnings(warnings) {
  clearOutdatedErrors();
  var isHotUpdate = !isFirstCompilation;
  isFirstCompilation = false;
  hasCompileErrors = false;

  function printWarnings() {
    // Print warnings to the console.
    var formatted = formatWebpackMessages({
      warnings: warnings,
      errors: []
    });

    if (typeof console !== 'undefined' && typeof console.warn === 'function') {
      for (var i = 0; i < formatted.warnings.length; i++) {
        if (i === 5) {
          console.warn('There were more warnings in other files.\n' + 'You can find a complete log in the terminal.');
          break;
        }

        console.warn(stripAnsi(formatted.warnings[i]));
      }
    }
  }

  printWarnings(); // Attempt to apply hot updates or reload.

  if (isHotUpdate) {
    tryApplyUpdates(function onSuccessfulHotUpdate() {
      // Only dismiss it when we're sure it's a hot update.
      // Otherwise it would flicker right before the reload.
      tryDismissErrorOverlay();
    });
  }
} // Compilation with errors (e.g. syntax error or missing modules).


function handleErrors(errors) {
  clearOutdatedErrors();
  isFirstCompilation = false;
  hasCompileErrors = true; // "Massage" webpack messages.

  var formatted = formatWebpackMessages({
    errors: errors,
    warnings: []
  }); // Only show the first error.

  ErrorOverlay.reportBuildError(formatted.errors[0]); // Also log them to the console.

  if (typeof console !== 'undefined' && typeof console.error === 'function') {
    for (var i = 0; i < formatted.errors.length; i++) {
      console.error(stripAnsi(formatted.errors[i]));
    }
  } // Do not attempt to reload now.
  // We will reload on next success instead.

}

function tryDismissErrorOverlay() {
  if (!hasCompileErrors) {
    ErrorOverlay.dismissBuildError();
  }
} // There is a newer version of the code available.


function handleAvailableHash(hash) {
  // Update last known compilation hash.
  mostRecentCompilationHash = hash;
} // Handle messages from the server.


connection.onmessage = function (e) {
  var message = JSON.parse(e.data);

  switch (message.type) {
    case 'hash':
      handleAvailableHash(message.data);
      break;

    case 'still-ok':
    case 'ok':
      handleSuccess();
      break;

    case 'content-changed':
      sendMessageToRoot('handleWebpackContentChanged', {}); // Triggered when a file from `contentBase` changed.

      window.location.reload();
      break;

    case 'warnings':
      handleWarnings(message.data);
      break;

    case 'errors':
      handleErrors(message.data);
      break;

    default: // Do nothing.

  }
}; // Is there a newer version of this code available?


function isUpdateAvailable() {
  /* globals __webpack_hash__ */
  // __webpack_hash__ is the hash of the current compilation.
  // It's a global variable injected by Webpack.
  return mostRecentCompilationHash !== __webpack_require__.h();
} // Webpack disallows updates in other states.


function canApplyUpdates() {
  return module.hot.status() === 'idle';
} // Attempt to update code on the fly, fall back to a hard reload.


function tryApplyUpdates(onHotUpdateSuccess) {
  if (false) {}

  if (!isUpdateAvailable() || !canApplyUpdates()) {
    return;
  }

  function handleApplyUpdates(err, updatedModules) {
    if (err || !updatedModules || hadRuntimeError) {
      window.location.reload();
      return;
    }

    if (typeof onHotUpdateSuccess === 'function') {
      // Maybe we want to do something.
      onHotUpdateSuccess();
    }

    if (isUpdateAvailable()) {
      // While we were updating, there was a new update! Do it again.
      tryApplyUpdates();
    }
  } // https://webpack.github.io/docs/hot-module-replacement.html#check


  var result = module.hot.check(
  /* autoApply */
  true, handleApplyUpdates); // // Webpack 2 returns a Promise instead of invoking a callback

  if (result && result.then) {
    result.then(function (updatedModules) {
      handleApplyUpdates(null, updatedModules);
    }, function (err) {
      handleApplyUpdates(err, null);
    });
  }
}

function sendMessageToRoot(type, payload) {
  window.parent.postMessage({
    // window.parent.parent.postMessage({
    source: window.name,
    // This is hard coded in the web project so we send it directly
    // The web doesn't expect to get a message from 2 levels below
    // source: 'preview-iframe',
    type: type,
    payload: payload
  }, '*');
}

/***/ }),

/***/ "./node_modules/css-loader/index.js?!./node_modules/postcss-loader/src/index.js?!./src/index.css":
/*!**************************************************************************************************************!*\
  !*** ./node_modules/css-loader??ref--5-oneOf-3-1!./node_modules/postcss-loader/src??postcss!./src/index.css ***!
  \**************************************************************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(/*! ../node_modules/css-loader/lib/css-base.js */ "./node_modules/css-loader/lib/css-base.js")(false);
// imports


// module
exports.push([module.i, "html {\n  height: 100%;\n}\n\nbody {\n  margin: 0;\n  height: 100%;\n  padding: 0;\n  font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", \"Roboto\", \"Oxygen\",\n    \"Ubuntu\", \"Cantarell\", \"Fira Sans\", \"Droid Sans\", \"Helvetica Neue\",\n    sans-serif;\n  -webkit-font-smoothing: antialiased;\n  -moz-osx-font-smoothing: grayscale;\n}\n\ncode {\n  font-family: source-code-pro, Menlo, Monaco, Consolas, \"Courier New\",\n    monospace;\n}\n\n#root {\n  display: flex;\n  height: 100%;\n}\n\n#anchor {\n  display: inline-flex;\n  margin: auto;\n}\n\n.console {\n  margin: 10px;\n}\n", ""]);

// exports


/***/ }),

/***/ "./src/App/index.js":
/*!**************************!*\
  !*** ./src/App/index.js ***!
  \**************************/
/*! exports provided: default */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "./node_modules/react/index.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
var _jsxFileName = "/capsule/src/App/index.js";

/* harmony default export */ __webpack_exports__["default"] = (react__WEBPACK_IMPORTED_MODULE_0___default.a.createElement("div", {
  className: "console",
  __source: {
    fileName: _jsxFileName,
    lineNumber: 3
  },
  __self: undefined
}));

/***/ }),

/***/ "./src/index.css":
/*!***********************!*\
  !*** ./src/index.css ***!
  \***********************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {


var content = __webpack_require__(/*! !../node_modules/css-loader??ref--5-oneOf-3-1!../node_modules/postcss-loader/src??postcss!./index.css */ "./node_modules/css-loader/index.js?!./node_modules/postcss-loader/src/index.js?!./src/index.css");

if(typeof content === 'string') content = [[module.i, content, '']];

var transform;
var insertInto;



var options = {"hmr":true}

options.transform = transform
options.insertInto = undefined;

var update = __webpack_require__(/*! ../node_modules/style-loader/lib/addStyles.js */ "./node_modules/style-loader/lib/addStyles.js")(content, options);

if(content.locals) module.exports = content.locals;

if(true) {
	module.hot.accept(/*! !../node_modules/css-loader??ref--5-oneOf-3-1!../node_modules/postcss-loader/src??postcss!./index.css */ "./node_modules/css-loader/index.js?!./node_modules/postcss-loader/src/index.js?!./src/index.css", function() {
		var newContent = __webpack_require__(/*! !../node_modules/css-loader??ref--5-oneOf-3-1!../node_modules/postcss-loader/src??postcss!./index.css */ "./node_modules/css-loader/index.js?!./node_modules/postcss-loader/src/index.js?!./src/index.css");

		if(typeof newContent === 'string') newContent = [[module.i, newContent, '']];

		var locals = (function(a, b) {
			var key, idx = 0;

			for(key in a) {
				if(!b || a[key] !== b[key]) return false;
				idx++;
			}

			for(key in b) idx--;

			return idx === 0;
		}(content.locals, newContent.locals));

		if(!locals) throw new Error('Aborting CSS HMR due to changed css-modules locals.');

		update(newContent);
	});

	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ "./src/index.js":
/*!**********************!*\
  !*** ./src/index.js ***!
  \**********************/
/*! no exports provided */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony import */ var _capsule_node_modules_babel_runtime_helpers_esm_objectSpread__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./node_modules/@babel/runtime/helpers/esm/objectSpread */ "./node_modules/@babel/runtime/helpers/esm/objectSpread.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "./node_modules/react/index.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! react-dom */ "./node_modules/react-dom/index.js");
/* harmony import */ var react_dom__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(react_dom__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var react_inspector__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! react-inspector */ "./node_modules/react-inspector/dist/es/react-inspector.js");
/* harmony import */ var _index_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ./index.css */ "./src/index.css");
/* harmony import */ var _index_css__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_index_css__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _App__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./App */ "./src/App/index.js");
/* harmony import */ var _serviceWorker__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./serviceWorker */ "./src/serviceWorker.js");

var _jsxFileName = "/capsule/src/index.js";







function Wrapper(_ref) {
  var Component = _ref.Component,
      className = _ref.className;
  return react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement("div", {
    id: "anchor",
    className: className,
    __source: {
      fileName: _jsxFileName,
      lineNumber: 10
    },
    __self: this
  }, react__WEBPACK_IMPORTED_MODULE_1___default.a.isValidElement(Component) ? Component : react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(Component, {
    __source: {
      fileName: _jsxFileName,
      lineNumber: 11
    },
    __self: this
  }));
}

function getInspector() {
  return react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(react_inspector__WEBPACK_IMPORTED_MODULE_3__["ObjectInspector"], {
    theme: Object(_capsule_node_modules_babel_runtime_helpers_esm_objectSpread__WEBPACK_IMPORTED_MODULE_0__["default"])({}, react_inspector__WEBPACK_IMPORTED_MODULE_3__["chromeLight"], {
      BASE_FONT_SIZE: 14,
      TREENODE_FONT_SIZE: 14
    }),
    data: _App__WEBPACK_IMPORTED_MODULE_5__["default"],
    __source: {
      fileName: _jsxFileName,
      lineNumber: 17
    },
    __self: this
  });
}

function getElement() {
  if (react__WEBPACK_IMPORTED_MODULE_1___default.a.isValidElement(_App__WEBPACK_IMPORTED_MODULE_5__["default"])) return react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(Wrapper, {
    Component: _App__WEBPACK_IMPORTED_MODULE_5__["default"],
    __source: {
      fileName: _jsxFileName,
      lineNumber: 24
    },
    __self: this
  });
  if (typeof _App__WEBPACK_IMPORTED_MODULE_5__["default"] === 'function') return react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(Wrapper, {
    Component: react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(_App__WEBPACK_IMPORTED_MODULE_5__["default"], {
      __source: {
        fileName: _jsxFileName,
        lineNumber: 25
      },
      __self: this
    }),
    __source: {
      fileName: _jsxFileName,
      lineNumber: 25
    },
    __self: this
  });
  ;
  return react__WEBPACK_IMPORTED_MODULE_1___default.a.createElement(Wrapper, {
    Component: getInspector(),
    className: "console",
    __source: {
      fileName: _jsxFileName,
      lineNumber: 27
    },
    __self: this
  });
}

function render() {
  return react_dom__WEBPACK_IMPORTED_MODULE_2___default.a.render(getElement(), document.getElementById('root'));
}

render(); // If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: http://bit.ly/CRA-PWA

_serviceWorker__WEBPACK_IMPORTED_MODULE_6__["register"]();

if (true) {
  module.hot.accept(/*! ./App */ "./src/App/index.js", function(__WEBPACK_OUTDATED_DEPENDENCIES__) { /* harmony import */ _App__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./App */ "./src/App/index.js");
(function () {
    render();
  })(__WEBPACK_OUTDATED_DEPENDENCIES__); });
}

/***/ }),

/***/ "./src/serviceWorker.js":
/*!******************************!*\
  !*** ./src/serviceWorker.js ***!
  \******************************/
/*! exports provided: register, unregister */
/***/ (function(module, __webpack_exports__, __webpack_require__) {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "register", function() { return register; });
/* harmony export (binding) */ __webpack_require__.d(__webpack_exports__, "unregister", function() { return unregister; });
// This optional code is used to register a service worker.
// register() is not called by default.
// This lets the app load faster on subsequent visits in production, and gives
// it offline capabilities. However, it also means that developers (and users)
// will only see deployed updates on subsequent visits to a page, after all the
// existing tabs open on the page have been closed, since previously cached
// resources are updated in the background.
// To learn more about the benefits of this model and instructions on how to
// opt-in, read https://bit.ly/CRA-PWA
var isLocalhost = Boolean(window.location.hostname === 'localhost' || // [::1] is the IPv6 localhost address.
window.location.hostname === '[::1]' || // 127.0.0.1/8 is considered localhost for IPv4.
window.location.hostname.match(/^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/));
function register(config) {
  if (false) { var publicUrl; }
}

function registerValidSW(swUrl, config) {
  navigator.serviceWorker.register(swUrl).then(function (registration) {
    registration.onupdatefound = function () {
      var installingWorker = registration.installing;

      if (installingWorker == null) {
        return;
      }

      installingWorker.onstatechange = function () {
        if (installingWorker.state === 'installed') {
          if (navigator.serviceWorker.controller) {
            // At this point, the updated precached content has been fetched,
            // but the previous service worker will still serve the older
            // content until all client tabs are closed.
            console.log('New content is available and will be used when all ' + 'tabs for this page are closed. See https://bit.ly/CRA-PWA.'); // Execute callback

            if (config && config.onUpdate) {
              config.onUpdate(registration);
            }
          } else {
            // At this point, everything has been precached.
            // It's the perfect time to display a
            // "Content is cached for offline use." message.
            console.log('Content is cached for offline use.'); // Execute callback

            if (config && config.onSuccess) {
              config.onSuccess(registration);
            }
          }
        }
      };
    };
  }).catch(function (error) {
    console.error('Error during service worker registration:', error);
  });
}

function checkValidServiceWorker(swUrl, config) {
  // Check if the service worker can be found. If it can't reload the page.
  fetch(swUrl).then(function (response) {
    // Ensure service worker exists, and that we really are getting a JS file.
    var contentType = response.headers.get('content-type');

    if (response.status === 404 || contentType != null && contentType.indexOf('javascript') === -1) {
      // No service worker found. Probably a different app. Reload the page.
      navigator.serviceWorker.ready.then(function (registration) {
        registration.unregister().then(function () {
          window.location.reload();
        });
      });
    } else {
      // Service worker found. Proceed as normal.
      registerValidSW(swUrl, config);
    }
  }).catch(function () {
    console.log('No internet connection found. App is running in offline mode.');
  });
}

function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(function (registration) {
      registration.unregister();
    });
  }
}

/***/ }),

/***/ 0:
/*!************************************************************!*\
  !*** multi ./config/webpackHotDevClient.js ./src/index.js ***!
  \************************************************************/
/*! no static exports found */
/***/ (function(module, exports, __webpack_require__) {

__webpack_require__(/*! /capsule/config/webpackHotDevClient.js */"./config/webpackHotDevClient.js");
module.exports = __webpack_require__(/*! /capsule/src/index.js */"./src/index.js");


/***/ })

},[[0,"runtime~main",0]]]);
//# sourceMappingURL=main.chunk.js.map