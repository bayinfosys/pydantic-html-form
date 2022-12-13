/*
 * js callbacks to allow collapsible elements for form simplication.
 *
 * no interaction with the backend.
 */
function collapsible(element_name) {
  // FIXME: get the maxheight setting of the first child, and make all subsequent the same
  let elements = document.getElementsByName(element_name);

  for (let i=0; i< elements.length; i++) {
    var content = elements[i];
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
  }
}
