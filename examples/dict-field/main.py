"""example of a model with a dict field creating a html form

the form will look rubbish with css styling
"""
import logging

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.DEBUG)

import pydantic
import pydform

from enum import Enum
from typing import List, Dict

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


#
# data classes
#
class UserType(str, Enum):
  """type enum to show dropdowns"""
  dog="dog"
  person="person"
  robot="robot"

class Address(pydantic.BaseModel):
  street: str
  city: str

class User(pydantic.BaseModel):
  """user class which stores some data"""
  name: str
  age: int
  type: UserType

  friends: Dict[str, int] # friends name and ages

  # addresses is a Dict with a user-defined key for the address
  addresses: Dict[str, Address]



#
# fast api setup
#
app = FastAPI()


templates = Jinja2Templates(directory="pydform/examples/dict-field")

def to_json(d):
  return d.json(indent=2)


templates.env.filters["to_json"] = to_json
templates.env.filters["asform"] = pydform.asform


@app.on_event("startup")
async def startup():
  app.state.user_list: List[User] = []


@app.get("/", response_class=HTMLResponse)
def get_users(request: Request):
  return templates.TemplateResponse(
      "template.html", {
          "request": request,
          "pydform_script_header": {
            "common": pydform.js.common_funcs,
            "submit": pydform.js.form_submission_script,
            "append": pydform.js.form_appendable_script,
            "collapse": pydform.js.collapsible_elements_script,
          },
          "users": request.app.state.user_list,
          "append_new_user": {
              "uri": request.url_for("post_new_user"),
              "name": "new-user",
              "model": User,
              "defaults": {}
          }
      }
  )


@app.post("/")
def post_new_user(request: Request, user: User):
  logger.info("recieved: '%s'", str(user.dict()))
  request.app.state.user_list.append(user)
