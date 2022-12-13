import logging
import pydantic

from typing import Optional, Any
from enum import Enum


logger = logging.getLogger(__name__)
logger.propagate = True


from .rtti import get_type_string, get_type_inner_info


class FieldDesc:
  """simple model to encapsulat the field info extracted from pydantic.typing
  """
  __slots__ = (
      "fieldname",
      "parent",
      "handler",
      "inner_name",
      "outer_type",
      "inner_type",
      "attributes"
  )

  def __init__(self, **kwargs):
    for k,v in kwargs.items():
      setattr(self, k, v)

    if not hasattr(self, "attributes"):
      setattr(self, "attributes", {})

  def asdict(self):
    return {k:getattr(self, k) for k in self.__slots__ if hasattr(self, k)}

  def qualified_name(self):
    return ".".join([x for x in [self.parent, self.fieldname] if x is not None])

  def __repr__(self):
    ignore=("outer_type","inner_type","attributes")
    return "FieldDesc(%s)" % ",".join(["%s=%s" % (k,v) for k,v in self.asdict().items() if k not in ignore])


def build_field_description(data: pydantic.fields.ModelField, parent=None) -> Optional[FieldDesc]:
  """build a dict which describes a field with all the stuff we need

     data: ModelField, pydantic model field datatype with annotations

     returns: dict, with info for html conversion (name, alias, default, required, and inner types for recursion)

     see: https://github.com/pydantic/pydantic/blob/main/pydantic/fields.py
  """
  # outer type is the container, or primitive
  # NB: get_origin returns None for BaseModel, so do `or getattr`
  outer_type=pydantic.typing.get_origin(data.outer_type_) or getattr(data, "outer_type_")
  outer_name=pydantic.typing.display_as_type(outer_type)
  # inner type is the container arg or primitive.
  inner_type=pydantic.typing.get_origin(data.type_) or getattr(data, "type_")
  inner_name=pydantic.typing.display_as_type(inner_type)

  sub_field_types = [x for x in data.sub_fields or []]
  sub_field_names = [pydantic.typing.display_as_type(x) for x in data.sub_fields or []]

#  logger.debug("[%s] data.outer_type_: '%s', data.type_: '%s'", data.name, str(data.outer_type_), str(data.type_))
#  logger.debug("[%s] outer_type: '%s', inner_type: '%s', sub_fields: '%s'", data.name, str(outer_type), str(inner_type), str(sub_field_types))
#  logger.debug("[%s] outer_name: '%s', inner_name: '%s', sub_names: '%s'", data.name, str(outer_name), str(inner_name), str(sub_field_names))

  handler = get_type_string(outer_type)
  inner_type, inner_name = get_type_inner_info(data, handler)

  attributes = {}

  if data.required:
    attributes.update({"required": ""})

  if data.default:
    attributes.update({"default": data.default})

  attributes.update({"alias": data.alias})

  if data.field_info.description:
#    logger.debug("[%s] descrip: '%s'", data.name, data.field_info.description)
    attributes.update({"placeholder": data.field_info.description})

#  logger.debug("[%s] dir: '%s'", data.name, str(dir(data)))
#  logger.debug("[%s] finfo: '%s'", data.name, str(dir(data.field_info)))
#  logger.debug("[%s] finfo.repr: '%s'", data.name, str(data.field_info.extra))
#  logger.debug("[%s] meta: '%s'", data.name, str(data.metadata))

  if "no_html" in data.field_info.extra:
    logger.warning("[%s] hidden by no_html attribute", data.name)
    return None

  return FieldDesc(
    fieldname = data.name,
    parent = parent,
    handler = get_type_string(outer_type),
    inner_name = inner_name,
    outer_type = outer_type,
    inner_type = inner_type,
    attributes = attributes,
  )
