/*
 * common functions for identifying keys/values, etc
 */
function iskey(a) {
  // predicate for deciding if a name fragment is a dict key
  return a.startsWith("_") && a.endsWith("-key");
}

function isvalue(a) {
  // predicate for deciding if a name fragment is a dict value
  return a.startsWith("_") && a.endsWith("-value");
}

function islist(a) {
  // predicate for deciding if a name fragment is a list
  return a.startsWith("_") && a.endsWith("-list");
}

function haskey(a) {
  // true if any fragment iskey
  return a.split(".").some(b => iskey(b));
}

function hasvalue(a) {
  // true if any fragmnet isvalue
  return a.split(".").some(b => isvalue(b));
}

function update_key(k, x, m) {
  // take a key k and insert x before the fragment m ("key" or "value")
  // eg: update_key("items-key", "test") -> "items-test-key"
  //     update_key("farm-value", "0x1") -> "farm-0x1-value"
  // update_key("label-key", "0x0") -> "label-0x0-key"
  return [].concat(k.split("-").slice(0, -1), [x, m]).join("-");
}
