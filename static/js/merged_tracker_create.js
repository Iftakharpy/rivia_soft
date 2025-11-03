import { deepCompare, removeAllEventListeners, stringFormat } from './utilities.js'
import { fetch_url, db_all_records, db_search_records } from './fetch_data.js'
import DATA from './parse_data.js'

let typingTimer;
let doneTypingInterval = 300;

let old_form = document.querySelector('form')
removeAllEventListeners(old_form)

let form = document.querySelector('form')

// Add event lister to query database on text input
let search_boxes = document.querySelectorAll('div[class="search_field"] > [name="search"]')
search_boxes.forEach((search_box) => {
  let search_field = search_box.parentElement
  let options_container = search_field.querySelector('div.select')
  // Add event listenners to update selected option
  for(let option of options_container.children){
    option.addEventListener('click', option_selected)
  }

  search_box.addEventListener('input', (event) => {
    // collect fields containing input and urls
    let search_field = event.currentTarget.parentElement
    let search_url_input_tag = search_field.querySelector('[name="search_url"]')
    let all_url_input_tag = search_field.querySelector('[name="all_url"]')
    let repr_format_pre_tag = search_field.querySelector('[name="repr_format"]')

    // separate info to search
    let search_text = event.currentTarget.value.trim()
    let search_url = search_url_input_tag.value
    let all_url = all_url_input_tag.value
    let repr_format = repr_format_pre_tag.value
    
    let select_element = search_field.querySelector('select')
    let options_container = search_field.querySelector('div.select')
    
    clearTimeout(typingTimer)
    typingTimer =  setTimeout(async (search_text, search_url, all_url, repr_format, select_element, options_container)=>{
      if(!deepCompare(search_text, '')){
        let records = await db_search_records(search_text, search_url)
        update_options(records, repr_format, select_element, options_container)
      }else{
        let records = await db_all_records(all_url)
        update_options(records, repr_format, select_element, options_container)
      }
    }, doneTypingInterval, search_text, search_url, all_url, repr_format, select_element, options_container)
  })
})
function update_options(records, repr_format, select_element, options_container, option_element_tag='span') {
  // clear options
  options_container.innerText = ''
  // select previously selected one default
  let currently_selected_option = select_element.options[select_element.selectedIndex]
  // if (currently_selected_option.value){
  //   let selected = document.createElement(option_element_tag)
  //   selected.classList.add('option')
  //   selected.classList.add('selected')
  //   selected.value = currently_selected_option.value
  //   selected.setAttribute('data-value', currently_selected_option.value)
  //   selected.textContent = currently_selected_option.textContent
  //   options_container.appendChild(selected)
  //   selected.addEventListener('click', option_selected)
  // }

  // update options
  for (let record of records){
    // create option
    let option = document.createElement(option_element_tag)
    option.value = record.pk
    option.setAttribute('data-value', record.pk)
    let string = repr_format.formatMultiplication(record)
    string = string.format(record)
    option.textContent = string
    // option.textContent = repr_format.format(record) // `👥{fields.client_name} 📁{fields.client_file_number} 📞{fields.personal_phone_number} ☎{fields.business_phone_number}`
    // add class
    option.classList.add('option')
    
    // add event listenner to this option
    option.addEventListener('click', option_selected)
    
    // add option in the select tag
    options_container.appendChild(option)
  }
}

//====================================================================================================================================
//
function option_selected(event) {
  // Options container
  let container = event.currentTarget.parentElement
  // Option clicked on
  let clicked_option = event.currentTarget
  if(clicked_option.hasAttribute('disabled')) return false
  clicked_option.classList.add('selected')

  let value = clicked_option.getAttribute('data-value')
  let text = clicked_option.textContent
  let options_container = clicked_option.parentElement
  let search_field = options_container.parentElement
  
  // Create option that is selected
  let selected_option = document.createElement('option')
  selected_option.textContent = text
  selected_option.value = value
  selected_option.setAttribute('data-value', value)
  
  // Clear select element
  let select_element = search_field.querySelector('select')
  select_element.innerText = ''
  // add option
  select_element.add(selected_option)

  // Update options_container
  options_container.innerText = ''
  // options_container.appendChild(clicked_option)

  // Update search_bar
  let search_bar = search_field.querySelector('[name="search"]')
  // search_bar.placeholder = text
  search_bar.value = text
  options_container.innerText = ''
  search_bar.focus()
  return true
}


let client_id_search_box = document.querySelector('form label[for="id_client_id"] + div input.search')
let client_id_search_box_parent = client_id_search_box.parentElement
let options_container = client_id_search_box.nextElementSibling
let selectElement = client_id_search_box_parent.querySelector('select')

removeAllEventListeners(client_id_search_box)

let client_id_search = client_id_search_box_parent.querySelector('input.search')

loadAllOptions()

client_id_search.addEventListener('input', (event)=>{
  let search_text = client_id_search.value || ''
  !search_text ? search_text='' : search_text = search_text.trim()
  clearTimeout(typingTimer)
  typingTimer = setTimeout(async ()=>{
    if (!search_text) loadAllOptions()
    else searchOptions(search_text)

    client_id_search.focus()
  }, doneTypingInterval)
})

options_container.addEventListener('click', (event)=>{
  let clickedOption = event.target
  if (!clickedOption.matches('.option')) return 

  let fromModel = clickedOption.getAttribute('data-model')
  form.action = DATA[fromModel].create_url

  
  let value = clickedOption.getAttribute('data-value')
  let text = clickedOption.textContent
  let selectOption = `<option value="${value}" selected>${text}</option>`
  
  selectElement.innerHTML = selectOption
  
  client_id_search.value = clickedOption.textContent
  client_id_search.focus()
})


async function searchOptions(search_text){
  let limited_records = db_search_records(search_text, DATA.Limited.search_url)
  let selfassesment_records = db_search_records(search_text, DATA.Selfassesment.search_url)
  
  Promise.all([limited_records, selfassesment_records]).then(data => {
    [limited_records, selfassesment_records] = data
    
    options_container.innerText = ''
    limited_records.forEach((record)=>{
      let option = createOption(record, 'Limited')
      options_container.appendChild(option)
    })
    selfassesment_records.forEach((record)=>{
      let option = createOption(record, 'Selfassesment')
      options_container.appendChild(option)
    })
  })
}

async function loadAllOptions(){
  let limited_all_records = db_all_records(DATA.Limited.viewall_url)
  let selfassesment_all_records = db_all_records(DATA.Selfassesment.viewall_url)
  
  Promise.all([limited_all_records, selfassesment_all_records]).then(data=> {
    [limited_all_records, selfassesment_all_records] = data
    
    options_container.innerText = ''
    limited_all_records.forEach((record)=>{
      let option = createOption(record, 'Limited')
      options_container.appendChild(option)
    })
    selfassesment_all_records.forEach((record)=>{
      let option = createOption(record, 'Selfassesment')
      options_container.appendChild(option)
    })
  })
}


function createOption(record, fromModel){
  let repr_format = DATA[fromModel].repr_format
  let option = document.createElement('span')
  option.value = record.pk

  let string = repr_format.formatMultiplication(record)
  string = string.format(record)
  option.textContent = string
  option.classList.add('option')

  option.setAttribute('data-model', fromModel)
  option.setAttribute('data-value', record.pk)
  return option
}
