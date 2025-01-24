from typing import Optional
import datetime as dt
from pydantic import BaseModel, Field, field_validator


class Manager(BaseModel):
    address: Optional[str]
    ceo: Optional[str]
    cfi_id: Optional[int] = Field(alias="cfiId")
    cfiLast_modification_datetime: Optional[str] = Field(alias="cfiLastModificationTime")
    is_completed: bool = Field(alias="isCompleted")
    manager_id: Optional[int] = Field(alias="managerId")
    manager_national_no: Optional[str] = Field(alias="managerNationalCode")
    manager_seo_register_no: Optional[str] = Field(alias="managerSeoRegisterNo")
    name: Optional[str]
    national_id: Optional[str] = Field(alias="nationalId")
    register_date: Optional[str] = Field(alias="registerDate")
    register_place: Optional[str] = Field(alias="registerPlace")
    register_place_id: Optional[str] = Field(alias="registerPlaceId")
    registered_capital: Optional[int] = Field(alias="registeredCapital")
    registration_number: Optional[str] = Field(alias="registrationNumber")
    seoRegisterDate: Optional[str] = Field("seo_register_date")
    tel: Optional[str]
    type: Optional[int]
    web_site: Optional[str] = Field(alias="webSite")


class FundItem(BaseModel):
    date: dt.date
    initiation_date: dt.date = Field(alias="initiationDate")
    name: str
    temp_guarantor_name: Optional[str] = Field(alias="tempGuarantorName")
    temp_manager_name: str = Field(alias="tempManagerName")
    type_of_invest: str = Field(alias="typeOfInvest")
    fund_type: int = Field(alias="fundType")
    manager: Manager
    dividend_interval_period: Optional[int] = Field(alias="dividendIntervalPeriod")
    # guarantor: Optional[str]
    fund_size: Optional[int] = Field(alias="fundSize")
    net_asset: Optional[int] = Field(alias="netAsset")
    reg_no: str = Field(alias="regNo")
    issue_nav: Optional[int] = Field(alias="issueNav")
    statistical_nav: Optional[int] = Field(alias="statisticalNav")
    cancel_nav: Optional[int] = Field(alias="cancelNav")

    @field_validator("date", mode="before")
    def parse_date(cls, value):
        return dt.datetime.fromisoformat(str(value)).date()


class DependencyGraph(BaseModel):
    items: list[FundItem]
