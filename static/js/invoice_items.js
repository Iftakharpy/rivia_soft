import { deepCompare, textToHTML } from '/static/js/utilities.js'
import { fetch_url, db_all_records, db_search_records } from '/static/js/fetch_data.js'



let typingTimer;
let doneTypingInterval = 300;

let items_in_invoice_data = document.querySelector('pre[name="items_in_invoice_data"]')
if (items_in_invoice_data) items_in_invoice_data = JSON.parse(items_in_invoice_data.textContent)
const INVOICE_ID = items_in_invoice_data?.invoice_id
let items_in_invoice = null
let invoice_items = null

await getAllItemsInInvoice(INVOICE_ID)
await showInvoiceItemsInInvoice(INVOICE_ID)

// =================================================================================================
// Handle search for invoice items
let search_box = document.querySelector('input[data-invoice-items-search]')
let search_field = search_box.parentElement
let options_container = search_field.querySelector('div.select')
let repr_format = items_in_invoice_data?.invoice_item?.repr_format
update_options(await getAllInvoiceItems(), repr_format, options_container)

search_box.addEventListener('input', (event) => {
  // separate info to search
  let search_text = event.currentTarget.value.trim()

  clearTimeout(typingTimer)
  typingTimer =  setTimeout(async (search_text, repr_format, options_container)=>{
    if(!deepCompare(search_text, '')){
      let records = await searchInvoiceItems(search_text)
      update_options(records, repr_format, options_container)
    }else{
      let records = await getAllInvoiceItems()
      update_options(records, repr_format, options_container)
    }
  }, doneTypingInterval, search_text, repr_format, options_container)
})


async function option_selected(event){
  let selected_option = event.currentTarget
  let invoice_item_id = selected_option.value
  
  let added_item_in_invoice = await addInvoiceItemToInvoice(INVOICE_ID, invoice_item_id)
  update_options(await getAllInvoiceItems(), repr_format, options_container)
  showInvoiceItemsInInvoice(added_item_in_invoice)
}
async function update_options(records, repr_format, options_container, option_element_tag='span') {
  // clear options
  options_container.innerText = ''
  items_in_invoice = await getAllItemsInInvoice(INVOICE_ID)
  
  // update options
  for (let record of records){
    let is_item_in_invoice = items_in_invoice.find(item=>item.fields.invoice_item_id===record.pk)
    if (is_item_in_invoice) continue
    // create option
    show_option(record, repr_format, options_container, option_element_tag)
  }
}

async function show_option(record, repr_format, options_container, option_element_tag='span'){
  // create option
  let option = document.createElement(option_element_tag)
  option.value = record.pk
  option.setAttribute('data-value', record.pk)
  
  let string = repr_format.formatMultiplication(record)
  string = string.format(record)

  option.textContent = string // `👥{fields.client_name} 📁{fields.client_file_number} 📞{fields.personal_phone_number} ☎{fields.business_phone_number}`

  // add class
  option.classList.add('option')
  
  // add event listenner to this option
  option.addEventListener('click', option_selected)
  
  // add option in the select tag
  options_container.appendChild(option)
}

// =================================================================================================
// Show invoice items in invoice
let timeoutInterval = 350 // 350ms
let timers = {
  'quantity': null,
  'rate': null,
  'vat_percent': null
}
async function showItemInInvoice(invoice_item_in_invoice){
  let {invoice_id, invoice_item_id, quantity, rate, vat_percent} = invoice_item_in_invoice.fields
  if (invoice_items===null) invoice_items = await getAllInvoiceItems()
  let invoice_item = invoice_items.find(item=>item.pk==invoice_item_id)

  let id = `invoice_${invoice_id}_invoice_item${invoice_item_id}`
  let quantity_id = `${id}_quantity`
  let rate_id = `${id}_rate`
  let vat_percent_id = `${id}_vat_percent`
  let delete_id = `${id}_delete`
  let invoice_item_markup = `<div class="invoice-item">
    <h2 class="service-name">${invoice_item.fields.name}</h2>
    <hr>
    <div class="cell">
      <label for="${quantity_id}">Quantity</label>
      <input id="${quantity_id}" type="number" step="1" min="1" value="${quantity}">
    </div>
    <div class="cell">
      <label for="${rate_id}">Rate</label>
      <input id="${rate_id}" type="number" value="${rate}">
    </div>
    <div class="cell">
      <label for="${vat_percent_id}">VAT(%)</label>
      <input id="${vat_percent_id}" type="number" value="${vat_percent}">
    </div>
    <div class="cell">
      <button id="${id}_delete" class="delete">Remove</button>
    </div>

  </div>`
  let invoice_item_node = textToHTML(invoice_item_markup)
  
  let quantity_input = invoice_item_node.querySelector(`#${quantity_id}`)
  let rate_input = invoice_item_node.querySelector(`#${rate_id}`)
  let vat_percent_input = invoice_item_node.querySelector(`#${vat_percent_id}`)
  let delete_button = invoice_item_node.querySelector(`#${id}_delete`)
  
  quantity_input.addEventListener('input', (event)=>{
    let quantity = event.currentTarget.value 
    let set_timer = timers['quantity']
    if (set_timer!==null) clearTimeout(set_timer)
    timers['quantity'] = setTimeout(() => updateInvoiceItemInInvoice(invoice_id, invoice_item_id, {quantity: quantity}), timeoutInterval)
  })
  rate_input.addEventListener('input', (event)=>{
    let rate = event.currentTarget.value
    let set_timer = timers['rate']
    if (set_timer!==null) clearTimeout(set_timer)
    timers['rate'] = setTimeout(() => updateInvoiceItemInInvoice(invoice_id, invoice_item_id, {rate: rate}), timeoutInterval)
  })
  vat_percent_input.addEventListener('input', (event)=>{
    let vat_percent = event.currentTarget.value

    let set_timer = timers['vat_percent']
    if (set_timer!==null) clearTimeout(set_timer)
    timers['vat_percent'] = setTimeout(() => updateInvoiceItemInInvoice(invoice_id, invoice_item_id, {vat_percent: vat_percent}), timeoutInterval)
  })
  delete_button.addEventListener('click', async (event)=>{
    await deleteInvoiceItemFromInvoice(invoice_id, invoice_item_id)
    await showInvoiceItemsInInvoice(invoice_id)
    update_options(await getAllInvoiceItems(), repr_format, options_container)
  })

  let invoice_items_in_invoice_container = document.querySelector('div.invoice-items-in-invoice')
  invoice_items_in_invoice_container.appendChild(invoice_item_node)
  return true
}

async function showInvoiceItemsInInvoice(invoice_id){
  let invoice_items_in_invoice_container = document.querySelector('div.invoice-items-in-invoice')
  invoice_items_in_invoice_container.innerText = ''
  await getAllItemsInInvoice(invoice_id)
  if (items_in_invoice===null || items_in_invoice.length==0 ) {
    invoice_items_in_invoice_container.innerHTML = 'No items in invoice'
    return
  }
  for (let item of items_in_invoice){
    showItemInInvoice(item)
  }
}


// =================================================================================================
// Fetch data from server
async function getAllInvoiceItems(){
  let url = items_in_invoice_data?.invoice_item?.all?.url
  let method = items_in_invoice_data?.invoice_item?.all?.request_method
  
  invoice_items = await db_all_records(url)
  return invoice_items
}
async function searchInvoiceItems(query){
  let url = items_in_invoice_data?.invoice_item?.search?.url
  let method = items_in_invoice_data?.invoice_item?.search?.request_method
  
  invoice_items = await db_search_records(query, url)
  return invoice_items
}

async function getAllItemsInInvoice(invoice_id, force_fetch=false){
  if (items_in_invoice!==null && !force_fetch) return items_in_invoice
  let url = items_in_invoice_data?.items_in_invoice?.all?.url.format({invoice_id: invoice_id})
  let method = items_in_invoice_data?.items_in_invoice?.all?.request_method
  
  let response = await fetch_url({url:url, req_method:method})
  items_in_invoice = await response.json()
  return items_in_invoice
}
async function addInvoiceItemToInvoice(invoice_id, invoice_item_id, data_object) {
  let url = items_in_invoice_data?.items_in_invoice?.create?.url.format({invoice_id: invoice_id, invoice_item_id: invoice_item_id})
  let method = items_in_invoice_data?.items_in_invoice?.create?.request_method
  
  let response = await fetch_url({url:url, req_method:method, data_object: data_object})
  let added_item_in_invoice = await response.json()
  items_in_invoice.push(added_item_in_invoice)
  return added_item_in_invoice
}
async function updateInvoiceItemInInvoice(invoice_id, invoice_item_id, data_object) {
  let item_to_update = findItemInInvoice(invoice_id, invoice_item_id)
  if (!item_to_update) return false
  data_object.invoice_id = invoice_id
  data_object.invoice_item_id = invoice_item_id
  
  let url = items_in_invoice_data?.items_in_invoice?.update?.url.format(item_to_update)
  let method = items_in_invoice_data?.items_in_invoice?.update?.request_method
  
  let response = await fetch_url({url:url, req_method:method, data_object: data_object})
  let item_in_invoice = await response.json()
  return item_in_invoice
}
async function deleteInvoiceItemFromInvoice(invoice_id, invoice_item_id) {
  let item_to_delete = findItemInInvoice(invoice_id, invoice_item_id)
  if (!item_to_delete) return false
  let url = items_in_invoice_data?.items_in_invoice?.delete?.url.format(item_to_delete)
  let method = items_in_invoice_data?.items_in_invoice?.delete?.request_method
  
  let response = await fetch_url({url:url, req_method:method})
  if (response.status >= 200 && response.status<=299) {
    items_in_invoice = items_in_invoice.filter(item=>item.fields.invoice_item_id!==invoice_item_id)
    return true
  }
  return false
}
function findItemInInvoice(invoice_id, invoice_item_id){
  return items_in_invoice.find(item=>item.fields.invoice_item_id == invoice_item_id && item.fields.invoice_id == invoice_id)
}

