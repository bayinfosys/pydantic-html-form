import logging
import pydantic


logger = logging.getLogger(__name__)
logger.propagate = True


#
# type info
#
# simple types
INPUT_TYPE_MAP = {
  "bool": "checkbox",
  "ConstrainedIntValue": "number",
  "ConstrainedFloatValue": "number",
  "datetime": "datetime-local",
  "enum": "select",
  "float": "number",
  "int": "number",
  "str": "text",
}

def is_primitive_type(typename):
  return typename in INPUT_TYPE_MAP

def get_type_string(class_type_):
  """convert a type to a string

     using `issubclass` internally, if this fails, uses `pydantic.typing.display_as_type`
  """
  import enum
  TYPES = {
    pydantic.BaseModel: "basemodel",
    list: "list",
    dict: "dict",
    enum.Enum: "enum"
  }

  try:
    for t, n in TYPES.items():
      if issubclass(class_type_, t):
        return n
  except (TypeError, KeyError):
    pass

  return pydantic.typing.display_as_type(class_type_)


def is_basemodel_type(class_type_):
  return get_type_string(class_type_) == "basemodel"
#
#def is_list_type(class_type_):
#  return get_type_string(class_type_) == "list"
#
def is_dict_type(class_type_):
  return get_type_string(class_type_) == "dict"

def is_enum_type(class_type_):
  return get_type_string(class_type_) == "enum"
#
#def is_union_type(typename: str):
#  return typename.lower() == "union" # fml

def get_type_inner_info(data, proc_type):
  """get the inner type info of data

     data: modelinfo data field
     proc_type: typename of the outer type

     returns: (inner_type, inner_name) a tuple with either (type, string) or (list[type], list[string]) depending on proc_type

     list, tuple return a scaler inner_type
     dict return a dict with "key" and "value" info
     union return a list of inner_types

     FIXME: make this handlers for the proc_type key
  """
  # inner type is the container arg or primitive.
  inner_type=pydantic.typing.get_origin(data.type_) or getattr(data, "type_")
  inner_name=pydantic.typing.display_as_type(inner_type)

  try:
    if proc_type == "list":
      if is_enum_type(inner_type):
        inner_name = "enum"
    elif proc_type == "dict":
      inner_type = {
        "key": pydantic.typing.get_args(data.outer_type_)[0],
        "value": pydantic.typing.get_args(data.outer_type_)[1]
       }

      inner_name = {
        "key": pydantic.typing.display_as_type(inner_type["key"]),
        "value": pydantic.typing.display_as_type(inner_type["value"])
      }
    elif proc_type in ("union", "Union"):
      inner_type = [x for x in data.sub_fields or []]
      inner_name = [pydantic.typing.display_as_type(x) for x in data.sub_fields or []]
    elif proc_type in ("tuple", "Tuple"):
      # tuple is similar to union/list, but not sure whether we use sub-fields or inner type
      # this seems to work for now
#      inner_type = [x for x in data.sub_fields or []]
#      inner_name = [pydantic.typing.display_as_type(x) for x in data.sub_fields or []]
      inner_type=pydantic.typing.get_origin(data.type_) or getattr(data, "type_")
      inner_name=pydantic.typing.display_as_type(inner_type)
    else:
#      logger.warning("[%s] inner type not processed", data.name)
      pass
  except TypeError as e:
    logger.error("[%s] unhandled type '%s' [%s]", data.name, str(data), str(e))
    raise e

  return inner_type, inner_name
