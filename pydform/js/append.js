/*
 * list/dict components allow elements to be added/removed
 *
 * new items are represented in the HTML as a `template` object
 * which is adjusted with new identifier values to distinguish
 * multiple entries.
 *
 * object-ids are just set by a random id (not incremented).
 * object-ids are swapped prior to submission with user-entered
 * key values.
 * object-id/name format is important: $object-$rnd-(key|value)
 *
 */
function duplicate_item(button_id, template_id, section_id) {
  // get the template
  let template = document.getElementById(template_id);

  let ns = template.content.cloneNode(true);

  // get a random suffix
  // FIXME: get a count of previous keys
  let random_suffix = Math.random().toString(36).substr(2, 5);
  let new_key = update_key(button_id, random_suffix, "key");
  let new_value = update_key(button_id, random_suffix, "value");
  let src_key = button_id;
  let src_value = button_id.replace("key", "value");

  console.log("new_key: " + new_key);
  console.log("new_value: " + new_value);

  // change the id tag in the template
  for (input_type of ["input", "select"]) {
    let inputs = ns.querySelectorAll(input_type);

    for (let i=0; i<inputs.length; i++) {
      let id_attr = inputs[i].getAttribute("id");
      console.log("id_attr: " + id_attr);

      if (haskey(id_attr)) {
        console.log("is_key('" + id_attr + "')");
        inputs[i].setAttribute("id", id_attr.replace(src_key, new_key));
        inputs[i].setAttribute("name", id_attr.replace(src_key, new_key));
      } else if (hasvalue(id_attr)) {
        console.log("is_key('" + id_attr + "')");
        inputs[i].setAttribute("id", id_attr.replace(src_value, new_value));
        inputs[i].setAttribute("name", id_attr.replace(src_value, new_value));
      } else {
        console.log("shiton");
      }
    }
  }

  let labels = ns.querySelectorAll("label");
  for (let i=0; i<labels.length; i++) {
    let for_attr = labels[i].getAttribute("for");

    if (haskey(for_attr)) {
      labels[i].setAttribute("for", for_attr.replace(src_key, new_key));
    } else if (hasvalue(for_attr)) {
      labels[i].setAttribute("for", for_attr.replace(src_value, new_value));
    } else {
      console.log("shiton");
    }
  }

  // update the parent html
  let section = document.getElementById(section_id);
  section.appendChild(ns);
}

function remove_item(e) {
  // delete a list item
  alert(e);
}
