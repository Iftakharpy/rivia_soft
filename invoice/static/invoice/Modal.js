// modal
const modalContainer = document.querySelector('#modal');
const modalBody = modalContainer.querySelector('.modal-body');
const modalCloseBtn = modalContainer.querySelector('.modal-header button');
modalCloseBtn.addEventListener('click', closeModal)
window.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
})


export function openModal(modalTitle, modalBodyNode){
    modalContainer.style.display = 'grid';
    modalContainer.querySelector('.modal-title').textContent = modalTitle;
    modalBody.appendChild(modalBodyNode);
}
export function closeModal(){
    modalContainer.style.display = 'none';
    modalBody.innerText = '';
}
