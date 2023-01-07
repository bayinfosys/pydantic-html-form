"""example of a model with a dict field creating a html form

the form will look rubbish with css styling
"""
import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

import pydantic
import pydform

from enum import Enum
from typing import List, Dict, Optional, Tuple, Union
from pydantic import BaseModel, Field

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

#
# enums
#
class ModelDataType(str, Enum):
  binary = "binary"
  category = "category"
  image = "image"
  keypoints = "keypoints"

class LossFunctions(str, Enum):
  auto = "auto"
  dice = "dice"
  focal = "focal"
  iou = "iou"
  jaccard = "jaccard"

#
# data classes
#
class ModelDataDefinition(BaseModel):
  """base class for defining model input and output data types"""
  # FIXME: Union[str, enum] fails
  type: ModelDataType
#  type: Union[str, ModelDataType]
#  type: Union[ModelDataType, str]

  shape: Optional[Tuple[int, ...]] = Field(
    None,
    description="shape of this input tensor; can be empty for category/binary values which can be infered"
  )

  loss: Union[LossFunctions, str] = Field(
#  loss: LossFunctions = Field(
    ...,
    description="loss function to apply to this output; if auto this is infered from the type"
  )


  class Config:
    use_enum_values = True

  metrics: List[Union[LossFunctions, str]] = Field(
    ["auto"],
    description="metrics applied to this output; if auto this is infered from the type"
  )

  class Config:
    use_enum_values = True


class TrainingDataDefinition(BaseModel):
  outputs: Dict[str, ModelDataDefinition] = Field(
    None,
    description="output definitions for the model"
  )

  class Config:
    use_enum_values = True


#
# fast api setup
#
app = FastAPI()


templates = Jinja2Templates(directory="examples/nested-basemodel")


def to_json(d):
  return d.json(indent=2)


templates.env.filters["to_json"] = to_json
templates.env.filters["asform"] = pydform.asform


@app.on_event("startup")
async def startup():
  app.state.data_list: List[TrainingDataDefinition] = []


@app.get("/", response_class=HTMLResponse)
def get_data(request: Request):
  logger.info("state: '%s'", str(request.app.state.data_list))
  return templates.TemplateResponse(
      "template.html", {
          "request": request,
          "pydform_script_header": {
            "common": pydform.js.common_funcs,
            "submit": pydform.js.form_submission_script,
            "append": pydform.js.form_appendable_script,
            "collapse": pydform.js.collapsible_elements_script,
          },
          "data": request.app.state.data_list,
          "append_new_data": {
              "uri": request.url_for("post_new_data"),
              "name": "new-user",
              "model": TrainingDataDefinition,
              "defaults": {}
          }
      }
  )


@app.post("/")
def post_new_data(request: Request, data: TrainingDataDefinition):
  logger.info("recieved: '%s'", str(data.dict()))
  request.app.state.data_list.append(data)
