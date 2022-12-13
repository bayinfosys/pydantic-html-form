/*
 * dict/list processing for form submission
 *
 * dictionaries which allow the user to enter key values require special
 * processing to make the user-value the key entry for the POST submission
 */
function inflate_form_data(fd) {
  // merges an object which is basically a list of key-values into a nested object
  // by splitting on the . character in key names
  // https://www.google.com/search?client=firefox-b-e&q=javascript+split+flat+keys+into+nested+
  let delim=".";
  return Object
    .entries(fd)
    .reduce((a, [k, v]) => {
      k.split(delim).reduce((r, e, i, arr) => {
        return r[e] || (r[e] = arr[i + 1] ? {} : v)
      }, a)

      return a
    }, {});
}

function get_key_names_from_object(d) {
  // get a list of dict keys from object keys
  return Object.keys(d)
    .filter(
      (key) => key.split(".").some(a => iskey(a)) && key.endsWith("-key")
    );
}

function get_value_names_from_object(d) {
  // get a list of dict values from object keys
  return Object.keys(d)
    .filter(
      (key) => key.split(".").some(a => isvalue(a)) && key.endsWith("-value")
    );
}

function get_list_names_from_object(d) {
  // get a list of list keys from object keys
  return Object.keys(d).filter((key) => key.split(".").some(a => islist(a)));
}

function map_keys(d) {
  // find and replace key placeholders with form values so we get
  // dicts with named entries for submission
  const key_names = get_key_names_from_object(d);

  console.log("key_names: " + key_names);

/*
  // create the replacement lut by isolating the key fragment and the value
  // NB: this fails when key.split.find is undefined
  const key_subs = Object.assign(...key_names.map(key => ({
    [key.split(".").find(a => iskey(a))]: d[key]
  })));
*/


  const key_subs = {};
  for (key_name of key_names) {
    if (haskey(key_name)) {
      key_subs[key_name.split(".").find(a => iskey(a))] = d[key_name];
    }
  }

  console.log({ key_subs });

  // remove the keys from the initial data
  key_names.forEach(a => delete d[a]);

  for ([key, value] of Object.entries(key_subs)) {
    for ([ak, av] of Object.entries(d)) {
      if (ak.includes(key)) {
        d[ak.replace(key, value)] = av;
        delete d[ak];
      }
    }
  }

  return d;
}

function map_values(d) {
  // find and replace value placeholders with form values so we get
  // dicts with named entries for submission. this is important when
  // dict values are primitive types and we don't have sub-keys to organise by.
  // this is slightly different from map_keys because we rename key entries
  // rather than create new entries.
  const value_names = get_value_names_from_object(d);

  console.log("value_names: " + value_names);

  for (value_key of value_names) {
    // find the key of the user entered key-value
    let actual_key = value_key.replace("value", "key");
    let user_key = d[actual_key];
    console.log("actual-key: '"+ actual_key + "' [" + user_key + "], value: " + value_key + " [" + d[value_key] + "]");

    // replace the temp name with the user-key
    let subkey = actual_key.split(".").filter(x => iskey(x))
    let new_key = actual_key.replace(subkey, user_key);
    console.log("new_key: '" + new_key + "'");
    d[new_key] = d[value_key];

    delete d[value_key];
    delete d[actual_key];
  }

  return d;
}

function map_lists(d) {
  // find and replace list placeholders with form values
  const list_names = get_list_names_from_object(d);

  list_names.forEach((key) => {
    const k = key.split(".").slice(0,-1).join(".");
    const v = d[key].split(",");
    delete d[key];
    d[k] = v;
  });

  return d;
}

function remove_zero_length_entries(d) {
  // remove the zero-length entries
  for (const [key, value] of Object.entries(d)) {
    if (value.length == 0) {
      delete d[key];
    }
  }
  return d;
}

function submit_form(e) {
  e.preventDefault();

  let form_object = new FormData(e.target);
  console.log(form_object);

  let form_data = Object.fromEntries(form_object.entries());
  console.log({ form_data });

  let zform_data = remove_zero_length_entries(form_data);
  console.log({ zform_data });

  // NB: values MUST be done before keys for primitve-typed nestings
  let vform_data = map_values(zform_data);
  console.log({ vform_data });

  let nform_data = map_keys(vform_data);
  console.log({ nform_data });

  let nnform_data = map_lists(vform_data);
  console.log({ nnform_data });

  let submission = inflate_form_data(nnform_data);
  console.log({ submission });

  let uri = form_data._uri;
  delete form_data["_uri"];
  console.log("POST:" + JSON.stringify(submission) + " to '" + uri + "'");

  fetch(uri, {
    method: "POST",
    headers: {"content-type": "application/json"},
    body: JSON.stringify(submission)
  })
    .then((data) => {
        console.log(data);
    })
    .catch((error) => {
        console.log("error:", error);
    }
  );

  return false;
}
