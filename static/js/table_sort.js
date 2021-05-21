//table cell compare attribute name = "data-cmp" from script.js

// find tables
let tables = document.querySelectorAll('table')
let compare_th_index = 0

tables.forEach(element => {
  let headers = element.querySelectorAll('th')
  // Add event listenners to table headers
  for (let th of headers){
    th.addEventListener('click', (event)=>{
      let th = event.currentTarget
      let reverse = th.getAttribute('reversed')
      let tbody = parentSelector(th, 'table').querySelector('tbody')
      compare_th_index = indexOfChildElement(th)
      
      // collect table rows
      let table_rows = parentSelector(th, "table").querySelectorAll('tbody tr')
      table_rows = Array.from(table_rows)
      // sort table rows
      table_rows = mergeSort(table_rows, reverse)

      // update table body
      tbody.innerHTML = ''
      for (let element of table_rows){
        tbody.appendChild(element)
      }

      if (reverse){
        th.removeAttribute('reversed')
      }else{
        th.setAttribute('reversed', true)
      }
    })
  }
});


// ===================================================================================
// Table header index finder
function indexOfChildElement(child){
  for(i = 0; (child = child.previousElementSibling); i++);
  return i
}

// Find parent element using selector
function parentSelector(child, selector){
  let parent = child.parentElement
  while(parent){
    if (parent.matches(selector)) return parent
    parent = parent.parentElement
  }
  return null
}

function AisSamller(a,b){
  let [val_a, val_b] = getCmpValue(a,b)
  return val_a < val_b
}
function AisGreater(a,b){
  let [val_a, val_b] = getCmpValue(a,b)
  return val_a > val_b
}

function getCmpValue(a,b){
  let val_a = a.children[compare_th_index].getAttribute('data-cmp')
  let val_b = b.children[compare_th_index].getAttribute('data-cmp')

  if (!val_a) val_a = a.children[compare_th_index].innerText
  if (!val_b) val_b = b.children[compare_th_index].innerText

  if (typeof(val_a) === 'string') val_a = val_a.trim()
  if (typeof(val_b) === 'string') val_b = val_b.trim()

  if (!val_a) val_a=''
  if (!val_b) val_b=''

  let num_a = parseFloat(val_a)
  let num_b = parseFloat(val_b)
  if (!isNaN(num_a) && num_a.toString().length==val_a.length) val_a = num_a
  if (!isNaN(num_b) && num_b.toString().length==val_b.length) val_b = num_b

  return [val_a, val_b]
}


// =====================================================================================================
// sort function
function _mergeArrays (a, b, reverse=false) {
  const c = []

  while (a.length && b.length) {
    // a[0] < b[0]
    // a[0] > b[0]
    reverse ? c.push(AisSamller(a[0], b[0]) ? b.shift() : a.shift()): c.push(AisGreater(a[0], b[0]) ? b.shift() : a.shift())
  }

  //if we still have values, let's add them at the end of `c`
  while (a.length) {
    c.push(a.shift())
  }
  while (b.length) {
    c.push(b.shift())
  }

  return c
}

function mergeSort(a, reverse=false){
  if (a.length < 2) return a
  const middle = Math.floor(a.length / 2)
  const a_l = a.slice(0, middle)
  const a_r = a.slice(middle, a.length)
  const sorted_l = mergeSort(a_l, reverse)
  const sorted_r = mergeSort(a_r, reverse)
  return _mergeArrays(sorted_l, sorted_r, reverse)
}

