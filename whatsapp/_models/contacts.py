from typing import Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, root_validator


class Address(BaseModel):
    country: str = Field(None, description="Full country name")
    city: Optional[str] = Field(None, description="City name")
    country_code: Optional[str] = Field(
        None, description="Two-letter country abbreviation"
    )
    state: Optional[str] = Field(None, description="State abbreviation")
    street: Optional[str] = Field(None, description="Street number and name")
    type: Optional[str] = Field(None, description="Standard Values: HOME, WORK")
    zip: Optional[str] = Field(None, description="ZIP code")


class Email(BaseModel):
    email: str
    type: Optional[str]


class Name(BaseModel):
    first_name: Optional[str] = Field(None, description="First name")
    formatted_name: str = Field(..., description="Full name as it normally appears")
    last_name: Optional[str] = Field(None, description="Last name")
    suffix: Optional[str] = Field(None, description="Name suffix")
    prefix: Optional[str] = Field(None, description="Name preffix")


class Org(BaseModel):
    company: Optional[str] = Field(None, description="Name of the contact's company")
    department: Optional[str] = Field(
        None, description="Name of the contact's department"
    )
    title: Optional[str] = Field(None, description="Contact's business title")


class Location(BaseModel):
    longitude: str = Field(..., description="Longitude of the location")
    latitude: str = Field(..., description="Latitude of the location")
    name: Optional[str] = Field(None, description="Name of the location")
    address: Optional[str] = Field(
        None, description="Address of the location. Only displayed if name is present."
    )


class Phone(BaseModel):
    type: Optional[str] = Field(
        None, description="Standard Values: CELL, MAIN, IPHONE, HOME, WORK"
    )
    phone: Optional[str] = None
    wa_id: Optional[str] = Field(None, description="WhatsApp ID")


class Url(BaseModel):
    url: Optional[str] = Field(None, description="URL")
    type: Optional[str] = Field(None, description="Standard Values: HOME, WORK")


## contact model


class Contact(BaseModel):
    addresses: Optional[List[Address]] = Field(
        None, description="Full contact address(es)"
    )
    birthday: Optional[str] = Field(None, description="YYYY-MM-DD formatted string")
    emails: Optional[List[Email]] = Field(None, description="Contact email address(es)")
    ims: Optional[List[str]] = Field(None, description="")
    name: Optional[Name] = None
    org: Optional[Org] = None
    phones: Optional[List[Phone]] = Field(None, description="Contact phone number(s)")
    urls: Optional[List[Url]] = Field(None, description="Contact URL(s)")
    contact_image: Optional[str] = Field(None, description="Contact image")

    # TODO: #69 move to base model
    @root_validator(pre=True)
    def remover_none_fields(cls, values: dict):
        return {k: v for k, v in values.items() if v}


class Contacts(BaseModel):
    __root__: List[Contact]
