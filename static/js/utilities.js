// Make markup safe(escape special characters)
export function makeSafeHTML(string){
  return string.replace(/&/g, "&amp;").replace(/>/g, "&gt;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
}

// Convert text to html node
export function textToHTML(html) {
  const template = document.createElement("template");
  template.innerHTML = html;
  return template.content;
}

//=======================================================================================================
// URL has query params
export function URL_HasQueryParams(url){
    let parsed_url = new URL(url, document.location)
    return Boolean(parsed_url.search.trim())
}
  

export function getAllUrlParams(url) {

    // get query string from url (optional) or window
    var queryString = url ? url.split('?')[1] : window.location.search.slice(1);
  
    // we'll store the parameters here
    var obj = {};
  
    // if query string exists
    if (queryString) {
  
      // stuff after # is not part of query string, so get rid of it
      queryString = queryString.split('#')[0];
  
      // split our query string into its component parts
      var arr = queryString.split('&');
  
      for (var i = 0; i < arr.length; i++) {
        // separate the keys and the values
        var a = arr[i].split('=');
  
        // set parameter name and value (use 'true' if empty)
        var paramName = a[0];
        var paramValue = typeof (a[1]) === 'undefined' ? true : a[1];
  
        // (optional) keep case consistent
        paramName = paramName.toLowerCase();
        if (typeof paramValue === 'string') paramValue = paramValue.toLowerCase();
  
        // if the paramName ends with square brackets, e.g. colors[] or colors[2]
        if (paramName.match(/\[(\d+)?\]$/)) {
  
          // create key if it doesn't exist
          var key = paramName.replace(/\[(\d+)?\]/, '');
          if (!obj[key]) obj[key] = [];
  
          // if it's an indexed array e.g. colors[2]
          if (paramName.match(/\[\d+\]$/)) {
            // get the index value and add the entry at the appropriate position
            var index = /\[(\d+)\]/.exec(paramName)[1];
            obj[key][index] = paramValue;
          } else {
            // otherwise add the value to the end of the array
            obj[key].push(paramValue);
          }
        } else {
          // we're dealing with a string
          if (!obj[paramName]) {
            // if it doesn't exist, create property
            obj[paramName] = paramValue;
          } else if (obj[paramName] && typeof obj[paramName] === 'string'){
            // if property does exist and it's a string, convert it to an array
            obj[paramName] = [obj[paramName]];
            obj[paramName].push(paramValue);
          } else {
            // otherwise add the property
            obj[paramName].push(paramValue);
          }
        }
      }
    }
  
    return obj;
  }

//=======================================================================================================
// Dayjs to work with Date object
dayjs.extend(window.dayjs_plugin_customParseFormat)

// datetime format
const time_zone = Intl.DateTimeFormat().resolvedOptions().timeZone // get user timezone
const time_format = "HH:mm"
const date_format = "DD-MM-YYYY"
const datetime_format = `${date_format} ${time_format}`

const search_date_format = "YYYY-MM-DD"
const search_time_format = "HH:mm:ss:SSS"
const search_datetime_format = `${date_format} ${time_format}`

// let date = dayjs()
// console.log(date.format(datetime_format))
// console.log(date.format(date_format))

export function dateFormat(date, raw_date_string){
    let formattedDate = ''
    // when raw_date_string.length > 10 it's a datetime
    // if (raw_date_string.length>10) formattedDate = date.toLocaleString()
    if (raw_date_string.length>10) formattedDate = date.format(datetime_format)
    
    // when raw_date_string.length == 10 it's a date
    // if (raw_date_string.length==10) formattedDate = date.toLocaleDateString()
    if (raw_date_string.length==10) formattedDate = date.format(date_format)

    // when raw_date_string.length < 10 it's a time
    // if (raw_date_string.length<10) formattedDate = date.toLocaleTimeString()
    if (raw_date_string.length<10) formattedDate = date.format(time_format)
    
    // //GMTString
    // console.log(date.toGMTString())
    // console.log(date.toGMTString().slice(0, 16))
    return formattedDate
}

//=======================================================================================================

// catch error and log
export function catchErrorAndLog(func, ...args){
  try{
    func(...args)
  }catch(error){
    let devLocations = ['127.0.0.1', 'localhost', '192.168.0']
    for(let location of devLocations){
      if(window.location.host.includes(location)){
        console.log(error)
        break
      }
    }
  };
}

export function removeAllEventListeners(element){
  let new_element = element.cloneNode(true);
  element.parentNode.replaceChild(new_element, element);
  return new_element
}


// Javascript object compare
export function deepCompare () {
  var i, l, leftChain, rightChain;

  function compare2Objects (x, y) {
    var p;

    // remember that NaN === NaN returns false
    // and isNaN(undefined) returns true
    if (isNaN(x) && isNaN(y) && typeof x === 'number' && typeof y === 'number') {
         return true;
    }

    // Compare primitives and functions.     
    // Check if both arguments link to the same object.
    // Especially useful on the step where we compare prototypes
    if (x === y) {
        return true;
    }

    // Works in case when functions are created in constructor.
    // Comparing dates is a common scenario. Another built-ins?
    // We can even handle functions passed across iframes
    if ((typeof x === 'function' && typeof y === 'function') ||
       (x instanceof Date && y instanceof Date) ||
       (x instanceof RegExp && y instanceof RegExp) ||
       (x instanceof String && y instanceof String) ||
       (x instanceof Number && y instanceof Number)) {
        return x.toString() === y.toString();
    }

    // At last checking prototypes as good as we can
    if (!(x instanceof Object && y instanceof Object)) {
        return false;
    }

    if (x.isPrototypeOf(y) || y.isPrototypeOf(x)) {
        return false;
    }

    if (x.constructor !== y.constructor) {
        return false;
    }

    if (x.prototype !== y.prototype) {
        return false;
    }

    // Check for infinitive linking loops
    if (leftChain.indexOf(x) > -1 || rightChain.indexOf(y) > -1) {
         return false;
    }

    // Quick checking of one object being a subset of another.
    // todo: cache the structure of arguments[0] for performance
    for (p in y) {
        if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
        }
        else if (typeof y[p] !== typeof x[p]) {
            return false;
        }
    }

    for (p in x) {
        if (y.hasOwnProperty(p) !== x.hasOwnProperty(p)) {
            return false;
        }
        else if (typeof y[p] !== typeof x[p]) {
            return false;
        }

        switch (typeof (x[p])) {
            case 'object':
            case 'function':

                leftChain.push(x);
                rightChain.push(y);

                if (!compare2Objects (x[p], y[p])) {
                    return false;
                }

                leftChain.pop();
                rightChain.pop();
                break;

            default:
                if (x[p] !== y[p]) {
                    return false;
                }
                break;
        }
    }

    return true;
  }

  if (arguments.length < 1) {
    return true; //Die silently? Don't know how to handle such case, please help...
    // throw "Need two or more arguments to compare";
  }

  for (i = 1, l = arguments.length; i < l; i++) {

      leftChain = []; //Todo: this can be cached
      rightChain = [];

      if (!compare2Objects(arguments[0], arguments[i])) {
          return false;
      }
  }

  return true;
}

function sleep(milliseconds) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
}

function sleepCallback(milliseconds, func, ...args) {
  const date = Date.now();
  let currentDate = null;
  do {
    currentDate = Date.now();
  } while (currentDate - date < milliseconds);
  func(...args)
}


//============================================================================================================


// source https://gist.github.com/poxip/90a9787be621eeddb82a
/**
 * Python-like string format function
 * @param {String} str - Template string.
 * @param {Object} data - Data to insert strings from.
 * @returns {String}
 */
 export function stringFormat(str, data) {
  let re = /{([^{}]+)}/g;

  return str.replace(re, function(match, val) {
    let prop = data;
    val.split('.').forEach(function(key) {
      prop = prop[key];
    });

    return prop;
  });
};


/**
 * Python-like format method
 * @param {Object} data - Data to insert strings from.
 * @returns {String}
*/
String.prototype.format = function(data) {
  return stringFormat(this, data);
};


/**
 * Python-like string multiplication with string format methods
 * @param {String} str - Template string.
 * @param {Object} data - Data to insert strings from.
 * @returns {String}
 */
 export function stringFormatMultiply(str, data) {
  let re = /\{("|')(?<string>.*?)\1\*(?<multiplicator>(?:\d+?|{(?<format_string>[^{}]+)}))\}/gm;
  let rv = str.replaceAll(re, function(...args) {
    let capturedGroups = args[args.length-1]
    let multiplicator = capturedGroups.multiplicator
    if ('format_string' in capturedGroups) multiplicator = multiplicator.format(data)
    return capturedGroups.string.repeat(multiplicator);
  });
  return rv
};

/**
 * Python-like string multiplication with string format methods
 * @returns {String}
*/
String.prototype.formatMultiplication = function(data) {
  return stringFormatMultiply(this, data); 
}