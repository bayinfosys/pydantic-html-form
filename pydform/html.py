import logging
import pydantic


logger = logging.getLogger(__name__)
logger.propagate = True


from .fielddesc import FieldDesc, build_field_description
from .rtti import INPUT_TYPE_MAP, is_primitive_type, is_dict_type, get_type_string, is_basemodel_type


HANDLERS = {
  # primitive types
  "bool": lambda name, d: html_for_single_type(name, d),
  "datetime": lambda name, d: html_for_single_type(name, d),
  "float": lambda name, d: html_for_single_type(name, d),
  "int": lambda name, d: html_for_single_type(name, d),
  "str": lambda name, d: html_for_single_type(name, d),

  # option types
#  "enum": lambda name, d: html_for_enum_type(name, d),
  "enum": lambda name, d: html_select_for_enum_type(name, d),

  # constrained values
  "ConstrainedFloatValue": lambda name, d: html_for_constrained_type(name, d),
  "ConstrainedIntValue": lambda name, d: html_for_constrained_type(name, d),

  # nested types
  "basemodel": lambda name, d: html_for_basemodel_type(name, d),
  "dict": lambda name, d: html_for_dict_type(name, d),
  "list": lambda name, d: html_for_list_type(name, d),
  "Union": lambda name, d: html_for_union_type(name, d),
  "tuple": lambda name, d: html_for_list_type(name, d),
}


class HTMLConversionException(Exception):
  pass

class HTMLAttributeCreationError(HTMLConversionException):
  pass

class PYDUnhandledTypeError(Exception):
  pass


#
# html string emission
#
def make_tag(name: str, attrs: dict = None, content: str = None) -> str:
  """build a html tag with attributes and content

     name: str, tagname
     attrs: dict[str, str], attributes and values to include in the opening tag
     content: string to include between the tag

     returns string containing a html fragment
  """
  # FIXME: if the content is None, emit a self-closing tag
  if attrs is not None:
    try:
      attr_list =["%s='%s'" % (k, v) for k,v in attrs.items() if len(str(v)) > 1]
      attr_list+=[k for k,v in attrs.items() if len(str(v)) == 0]
    except TypeError as e:
      #logger.exception("failed to build attributes from '%s' [%s]", str(attrs), str(e))
      raise HTMLAttributeCreationError from e

    # NB: add a leading space to separate from the tagname
    attrs = " ".join(attr_list)

  # FIXME: if attrs is empty we have a trailing space after the tag name
  return """<{tag} {attrs}>{content}</{tag}>""".format(
      tag=name,
      attrs=attrs or "",
      content=content or ""
  )


def html_for_single_type(name, d: FieldDesc, *, id=None, label_content=None):
  """handler for basic types (int, float, str, etc)

     name: str, text to display for this form element
     d: datatype information to render the element

     returns str html fragment

     TODO: name and form-id should be different
  """
  el_id = d.qualified_name()
  el_name = el_id
  el_content = label_content or d.attributes.get("alias") or name

  attrs = dict(
    type=INPUT_TYPE_MAP[d.handler],
    id=el_id,
    name=el_name,
  )

  if d.attributes.get("default"):
    attrs.update({"value": d.attributes.get("default")})

  if d.attributes.get("required"):
    attrs.update({"required": ""})

  if d.attributes.get("placeholder"):
    attrs.update({"placeholder": d.attributes["placeholder"]})

  return "".join((
      make_tag("label", attrs={"for": el_id}, content=el_content),
      make_tag("input", attrs)
  ))


def html_select_for_enum_type(name, d: FieldDesc):
  """convert an enum type to a html select dropdown"""
#  id = ".".join([x for x in (d["parent"], d["fieldname"]) if x is not None])
  el_id = d.qualified_name()
  el_name = el_id

  print(d.inner_type)
  print(",".join([e.value for e in d.inner_type]))

  # FIXME: add required to select
  # FIXME: default value
  select_group = "".join([make_tag("option", attrs=dict(value=e.value), content=e.value) for e in d.inner_type])

  print(select_group)

  return "".join((
      make_tag("label", attrs={"for": el_name}, content=name),
      make_tag("select", attrs={"name": el_name, "id": el_id}, content=select_group)
  ))


def html_radio_group_for_enum_type(name, d: FieldDesc, *, required=False):
  """convert an enum type to a html radio group"""
  radio_group = "".join([
      html_for_single_type(name,
          FieldDesc(fieldname=name, handler="enum"),
          id=e.value
      ) for e in d.inner_type
  ])

  return """<fieldset><legend>{name}</legend>{inputs}</fieldset>""".format(
    name=name,
    inputs=radio_group
  )


def html_for_constrained_type(name, d):
  """handler for constrained types which adds range bounds to the html controls

     TODO
  """
  logger.warning("Constrained*Value converted to HTML with no range values")
  return html_for_single_type(name, d)


def html_for_primitive_type(name, d: FieldDesc, **kwargs):
  """convert a primitive type (str, int, etc) to HTML

     name: str, name of the type

     # FIXME: remove
  """
  if d.handler == "enum":
    return html_select_for_enum_type(name, d)
  elif d.handler in ("str", "int", "datetime", "bool", "float"):
    return html_for_single_type(name, d, **kwargs)
  elif d.handler in ("ConstrainedIntValue", "ConstrainedFloatValue"):
    return html_for_constrained_type(name, d)
  else:
    logger.warning("[%s] unhandled primitve type '%s'", name, str(d.handler))
    raise PYDUnhandledTypeError


#
# convert types to html
#
def html_for_dict_type(name, d: FieldDesc):
  """convert a dict to HTML

     this type requires an editable key-value pair
     and new key types to be created in the front end

     NB: the `key` elements name-attribute are formatted `_<fieldname>-key`
     `value` elements name-attribute are formatted `_<fieldname>-key-value`
     the .js component removes the key elements from the form and replaces
     the `value` name string with the value of the `_<fieldname>-key` element
     so we can construct dicts with key values entered by users. difficult.
  """
  fieldname = "_%s-key" % d.fieldname
  parentname = d.fieldname
  attrs = d.attributes

  # create the key type placeholder
  if is_primitive_type(d.inner_name["key"]):
    f = FieldDesc(
      fieldname=fieldname,
      parent=d.fieldname,
      inner_type=d.inner_type["key"],
      inner_name=d.inner_name["key"],
      handler = get_type_string(d.inner_type["key"]),
      attributes={**{"default": "01"}, **attrs},
    )
    # NB: using d.inner_name[value] here means dict types will use the inner name
    # as the reference (usually this is a nice mnemoic "address" for "addresses" container)
    # but it might look shit at other times.
    if is_primitive_type(d.inner_name["value"]) or is_dict_type(d.inner_type["value"]):
      label_content="reference"
    elif is_basemodel_type(d.inner_type["value"]):
      label_content=d.inner_name["value"]
    else:
      label_content=None

    keys_html = html_for_primitive_type(f"{name}-key", f, label_content=label_content)
  else:
    logger.warning("[%s] no input for dict fields", name)
    keys_html = """<div>KEYTYPE</div>"""

  # create the value type form
  if is_primitive_type(d.inner_name["value"]):
    f = FieldDesc(
      fieldname="_%s-value" % d.fieldname,
      parent=d.fieldname,
      inner_type=d.inner_type["value"],
      inner_name=d.inner_name["value"],
      handler=d.inner_name["value"],
      attributes=attrs,
    )

    print("f: %s" % str(f))
    values_html = html_for_primitive_type(f"{name}-value", f, label_content="value")
  elif is_basemodel_type(d.inner_type["value"]):
    f = FieldDesc(
      fieldname=fieldname,
      parent=d.fieldname,
      inner_type=d.inner_type["value"],
      inner_name=d.inner_name["value"],
      handler="basemodel",
      attributes = attrs,
    )
    values_html = html_for_basemodel_type(name, f)
  elif is_dict_type(d.inner_type["value"]):
    logger.debug("[%s] %s", name, str(d))

    f = FieldDesc(
      fieldname=fieldname,
      parent=d.fieldname,
      inner_type=d.inner_type["value"],
      inner_name=d.inner_name["value"],
      handler="basemodel",
#      handler="dict",
      attributes = attrs,
    )
    values_html = html_for_dict_type(name, d)
  else:
    logger.warning("unhandled inner-name: '%s'", str(d.inner_type["value"]))
    return "[%s]ERROR[%s]" % (name, "dict")

  return """
<section id='{name}-section'>
<h3 onclick="collapsible('{name}-items'); return false;">{name}</h3>
<div>
<a id='{name}-add-button' href='#' onclick='duplicate_item("{fieldname}", "{name}-template", "{name}-section"); return false;'>add</a>
</div>
<template id='{name}-template'>
<fieldset name='{name}-items' class='collapsible'>
{keys}{values}
<a id='{name}-remove-button' href='#' onclick='remove_item("{fieldname}", "{name}-template", "{name}-section"); return false;'>remove</a>
</fieldset>
</template>
</section>
""".format(
    fieldname=fieldname,
    name=name,
    keys=keys_html,
    values=values_html
  )


def html_for_list_type(name, d: FieldDesc):
  """convert a list to HTML

     name: str, reference name to use in the form id
     d: type object, type info

     return: str, html fragment for list entry

     # FIXME: this item is a placeholder for items appended to a list
     # FIXME: set the id as `new-value` and on edit commit that change to the form
  """
#  logger.info("d: '%s'", str(d))
  fieldname = "_%s-list" % d.fieldname

  # FIXME: check the list values are primitive
  if is_primitive_type(d.inner_name):
    # FIXME: use HANDLERS
    f=FieldDesc(
      fieldname = fieldname,
      parent = d.qualified_name(),
      handler = "str", #d.inner_name,
      outer_type = type(str), #d.inner_type,
      inner_name = "str", #d.inner_name,
      inner_type = type(str), #d.inner_type,
      attributes = {},
    )
    values_html = html_for_primitive_type(fieldname, f)
  else:
    logger.warning("unhandled inner-name: [%s] '%s'", d.inner_name, str(d.inner_type))
    return "[%s]ERROR[%s]" % (name, "list")

  return """<section><h3>{name}</h3></section>{values}""".format(
    name=name,
    values=values_html
  )


def html_for_basemodel_type(name, d: FieldDesc):
  """output html for a basemodel
  """
  p = d.qualified_name()

  try:
    values_html = "".join([convert_property(field, parent=p) for _, field in d.inner_type.__fields__.items()])
  except (AttributeError, TypeError) as e:
    logger.exception("%s [%s]", str(d), str(e))
    values_html = "NONE"

# NB: the header is off-putting in this format
#  return """<section><h3>{name}</h3></section>{values}""".format(
#    name=d.inner_name,
#    values=values_html
#  )

  return values_html


def html_for_union_type(name: str, d: FieldDesc):
  """convert a union to HTML

     name: name of the field
     d: type info object

     FIXME: I have no idea how to handle a union in the UI; we should have a tabbed element
            with each tab having the different type in the union, but this requires some js
            and makes form submission difficult. For now we just take the first element.
  """
  assert isinstance(d.inner_type, list)

  p = d.qualified_name()

  vals = [convert_property(alt, parent=p) for idx, alt in enumerate(d.inner_type)]

  return """<section><h3>{name}</h3></section>{values}""".format(
    name=name,
    values=vals[0]
  )


def convert_property(data: pydantic.fields.ModelField, parent=None):
  """convert a pydantic ModelField type to HTML

     this is different to the python type handlers because it emits
     a `fieldset` tag with the name of the field in the legend.
     python type handlers simply emit the form elements
  """
  assert isinstance(data, pydantic.fields.ModelField)

  # identify the type of the field
  try:
    field_desc = build_field_description(data, parent=parent)
  except TypeError as e:
    logger.error("[%s] bad type: '%s' [%s]", data.name, str(data), str(e))
    return "[%s]ERROR[%s]" % (data.name, str(data))

#  logger.debug("[%s]: %s", data.name, str(field_desc))

  if field_desc is None:
    return ""

  # process the type we discovered
  try:
    return HANDLERS[field_desc.handler](data.name, field_desc)
  except KeyError as e:
    logger.error("[%s] no handler for type '%s' [%s]", data.name, field_desc.handler, str(e))
