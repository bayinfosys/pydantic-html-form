import logging
import pydantic


logger = logging.getLogger(__name__)
logger.propagate = True

from .fielddesc import build_field_description
from pydform.html import HANDLERS, convert_property, make_tag

#
# jinja entry point
#
def asform(value):
  """jinja compatible method to convert a pydantic.BaseModel derived class to HTML

     value must contain keys:
     + model: pydantic model for conversion
     + uri: target uri for submission (POST as JSON object)
     + defaults: initial values to put in the form
  """
  assert isinstance(value["model"], pydantic.main.ModelMetaclass)
  assert isinstance(value["uri"], str)

  uri = value["uri"]

  logger.info("posting to '%s'", uri)

  form_content = "".join([
      convert_property(v)
      for _,v in value["model"].__fields__.items()
  ]+[
      make_tag("label", attrs={"for": "_submit"}, content="submit"),
      make_tag("input", attrs={"type": "submit", "id": "_submit"}),
      make_tag("input", attrs={"type": "hidden", "id": "_uri", "name": "_uri", "value": uri})
  ])

  return make_tag(
      "form",
      attrs={
        "onsubmit": "return submit_form(event)",
        "name": "myform"
      },
      content=form_content
  )
