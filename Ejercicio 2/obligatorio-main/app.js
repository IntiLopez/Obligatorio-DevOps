function showModal() {
    document.getElementById('modal-bg').classList.add('active');
}
function hideModal() {
    document.getElementById('modal-bg').classList.remove('active');
    return true;
}
function showEditModal(id, nombre, email) {
    document.getElementById('edit_id').value = id;
    document.getElementById('edit_nombre').value = nombre;
    document.getElementById('edit_email').value = email;
    document.getElementById('edit-modal-bg').classList.add('active');
}
function hideEditModal() {
    document.getElementById('edit-modal-bg').classList.remove('active');
    return true;
}
