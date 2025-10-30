import { fetch_url, db_all_records, db_search_records, db_search_records_client_id } from './fetch_data.js'
import { populate_with_merged_data } from './table.js'
import { removeAllEventListeners } from './utilities.js'
import DATA from './parse_data.js'
import merge from './merged_tracker_sort_by_deadline.js';

loadAllTrackers()

const Limited = DATA.Limited
const limited_template_query_string = 'template#limited_tracker_template'
const Selfassesment = DATA.Selfassesment
const selfassesment_template_query_string = 'template#selfassesment_tracker_template'

// // Merged tracker Create Options
// const create_btn = document.querySelector('#merged_tracker_create')
// const create_options = document.querySelector('#create_options_container')
// const create_options_close_btn = document.querySelector('#merged_tracker_create_options_close')

// create_btn.addEventListener('click', (event) => {
//   event.preventDefault()
//   create_options.style.display = 'flex'
// })

// create_options_close_btn.addEventListener('click', (event)=>{
//   event.preventDefault()
//   create_options.style.display = 'none'
// })

//table cell compare attribute name = "data-cmp"

// clear messsage after 10 seconds
let delete_message_after = 10000 //milisecond
setTimeout(function(){
  let messages = document.querySelectorAll('.message')
  if (messages){
    for (let element of messages){
      element.remove()
    }
  };
}, delete_message_after);

// ================================================================================================
// Handle reload
document.querySelector('.action-reload').addEventListener('click', async (event) => {
  loadAllTrackers()
})

// Search functionality
//setup before functions
let typingTimer;                  //timer identifier
//                miliseconds * seconds
let doneTypingInterval = 1000;//time in ms (4/5 seconds)
//on keyup, start the countdown
// document.getElementById('element-id').addEventListener('keyup', () => {
//     clearTimeout(typingTimer);
//     if (myInput.value) {
//         typingTimer = setTimeout(search_function, doneTypingInterval);
//     }
// });
const tax_year_select_input = document.querySelector('select#tax_years')
const search_bar = document.querySelector('[name="search"]');
function searchHandler(){
  let limited_search_url = Limited.search_url
  let selfassesment_search_url = Selfassesment.search_url

  let search_text = search_bar.value.trim()

  // reset timer to prevent extra search
  clearTimeout(typingTimer);
  // set the timer again to call api after doneTypingInterval
  if (search_text===''){
    typingTimer = setTimeout( async () => {
      loadAllTrackers()
    }, doneTypingInterval); // Get all the records
  }else{
    searchTrackers(doneTypingInterval, search_text, limited_search_url, selfassesment_search_url)
  }
}
if (search_bar){ search_bar.addEventListener('input', searchHandler) }
if (tax_year_select_input){ tax_year_select_input.addEventListener('input', searchHandler) }

export function loadAllTrackers(){
  setTimeout(async ()=>{
    let limited_all_records = db_all_records(Limited.viewall_url)
    let selfassesment_all_records = db_all_records(Selfassesment.viewall_url)
    
    Promise.all([limited_all_records, selfassesment_all_records]).then(data=>{
      let [limited_all_records, selfassesment_all_records] = data
      let merged = merge(limited_all_records, selfassesment_all_records, true)

      populate_with_merged_data(
        merged,
        selfassesment_template_query_string,
        Selfassesment.model_fields,
        Selfassesment.update_url,
        Selfassesment.delete_url,
        limited_template_query_string,
        Limited.model_fields,
        Limited.update_url,
        Limited.delete_url,
        true
        )
    })
  }, 0); // search with text
}

export function searchTrackers(doneTypingInterval, search_text, limited_search_url, selfassesment_search_url){
  typingTimer = setTimeout(async (search_text, limited_search_url, selfassesment_search_url)=>{
    let limited_search_records = db_search_records(search_text, limited_search_url)
    let selfassesment_search_records = db_search_records(search_text, selfassesment_search_url)

    Promise.all([limited_search_records, selfassesment_search_records]).then(data=>{
      let [limited_search_records, selfassesment_search_records] = data
      let merged = merge(limited_search_records, selfassesment_search_records)

      populate_with_merged_data(
        merged,
        selfassesment_template_query_string,
        Selfassesment.model_fields,
        Selfassesment.update_url,
        Selfassesment.delete_url,
        limited_template_query_string,
        Limited.model_fields,
        Limited.update_url,
        Limited.delete_url,
        true
        )
    })
  }, doneTypingInterval, search_text, limited_search_url, selfassesment_search_url); // search with text
}


let task_container = document.querySelector('.task-container')
let tasks = task_container.querySelectorAll('.task')
for (let task of tasks){
  task = removeAllEventListeners(task)
  task.addEventListener('click', async (event) => {
    let task = event.currentTarget
    let param = task.getAttribute('data-tasks')
  
    // prepare url to fetch
    let params = {tasks: param, tax_year: DATA.tax_year}
    // params['q'] = 'ifta'

    let search_param = new URLSearchParams(params).toString()

    let limited_search_records = searchTrackersTasks(Limited.search_url, search_param)
    let selfassesment_search_records = searchTrackersTasks(Selfassesment.search_url, search_param)
    
    Promise.all([limited_search_records, selfassesment_search_records]).then(data=>{
      let [limited_search_records, selfassesment_search_records] = data
      let merged = merge(limited_search_records, selfassesment_search_records)

      populate_with_merged_data(
        merged,
        selfassesment_template_query_string,
        Selfassesment.model_fields,
        Selfassesment.update_url,
        Selfassesment.delete_url,
        limited_template_query_string,
        Limited.model_fields,
        Limited.update_url,
        Limited.delete_url,
        true
        )
    
      let counts = task.querySelector('#task-count')
      counts.innerHTML = merged.length
    })
  })
}


async function searchTrackersTasks(
  search_url,
  search_param){
  let url = `${search_url}?${search_param}`
  
  let kwargs = {
    url: url,
    req_method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  }
  let response = await fetch_url(kwargs)
  let data = await response.json()
  return data
}
