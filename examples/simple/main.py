"""example of a simple model creating a html form

the form will look rubbish with css styling
"""
import logging

import pydantic
import pydform

from enum import Enum
from typing import List

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates


logger = logging.getLogger("uvicorn")


#
# data classes
#
class UserType(str, Enum):
  """type enum to show dropdowns"""
  dog="dog"
  person="person"
  robot="robot"


class User(pydantic.BaseModel):
  """user class which stores some data"""
  name: str
  age: int
  type: UserType


#
# fast api setup
#
app = FastAPI()


templates = Jinja2Templates(directory="pydform/examples/simple")
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
            "submit": pydform.js.form_submission_script,
            "append": pydform.js.form_appendable_script,
            "collapse": pydform.js.collapsible_elements_script
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
