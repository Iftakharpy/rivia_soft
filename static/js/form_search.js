import { deepCompare } from './utilities.js'
import { fetch_url, db_all_records, db_search_records } from './fetch_data.js'


let typingTimer;
let doneTypingInterval = 300;

// find all searchable select fields
let select_elements = document.querySelectorAll('div[class="search_field"] > div.select')

// add event listeners on searchable select fields
select_elements.forEach(element => {
  // add event listenner to each item
  element.addEventListener('change', (event) => {
    // get select tag from event
    let select = event.currentTarget
    // get previous sibling input tag
    let search_box = select.previousElementSibling

    // update placeholder to currently selected value
    let selected_option_text = select.options[select.selectedIndex].textContent
    // search_box.placeholder = selected_option_text
    // search_box.value = selected_option_text
  })
}); 

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
  options_container.innerHTML = ''
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
    option.textContent = repr_format.format(record) // `👥{fields.client_name} 📁{fields.client_file_number} 📞{fields.personal_phone_number} ☎{fields.business_phone_number}`
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
  select_element.innerHTML = ''
  // add option
  select_element.add(selected_option)

  //Old
  // // Update options_container
  // clicked_option.remove()
  // if (options_container.firstElementChild){
  //   options_container.firstElementChild.classList.remove('selected')
  // }
  // options_container.prepend(clicked_option)
  //New according to requirements
  options_container.innerHTML = ''
  // options_container.appendChild(clicked_option)

  // Update search_bar
  let search_bar = search_field.querySelector('input[name="search"]')
  // search_bar.placeholder = text
  search_bar.value = text
  options_container.innerHTML = ''
  search_bar.focus()
  return true
}
