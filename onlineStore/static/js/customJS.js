function prevent_multi_submit(id_form, id_button) {
  if (document.getElementById(id_form).checkValidity() === false) {
    return;
  }

  document.getElementById(id_button).disabled = true;
  document.getElementById(id_form).submit();
}