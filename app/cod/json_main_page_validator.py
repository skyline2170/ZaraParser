import pydantic
import loguru
import dataclasses

loguru.logger.remove()
loguru.logger.add("log_validate_error.log", level="ERROR")


@dataclasses.dataclass()
class Top_bar_main_page:
    name: str
    id: int
    seo_category_id: int
    keyword: str


class _Seo_json(pydantic.BaseModel):
    seo_category_id: int = pydantic.Field(alias="seoCategoryId")
    keyword: str


class _Categories_json(pydantic.BaseModel):
    id: int
    seo: _Seo_json
    name: str


class _Top_bar_json(pydantic.BaseModel):
    categories: list[_Categories_json]


class _Category_json(pydantic.BaseModel):
    topbar: _Top_bar_json


class _Main_json(pydantic.BaseModel):
    category: _Category_json


def top_bar_validator(raw_json: str) -> None | list[Top_bar_main_page]:
    try:
        json = _Main_json.parse_raw(raw_json)
        json = json.dict()
        # print(json)
        top_bar_list = []
        for i in json["category"]["topbar"]["categories"]:
            top_bar_list.append(Top_bar_main_page(id=i["id"],
                                                  seo_category_id=i["seo"]["seo_category_id"],
                                                  keyword=i["seo"]["keyword"],
                                                  name=i["name"]
                                                  ))
        # print(top_bar_list)
        # top_bar_list = [f"https://www.zara.com/tr/tr/{i.keyword}-l{i.seo_category_id}.html?v1={i.id}" for i in top_bar_list]
        # print(top_bar_list)
        return top_bar_list[:]
    except pydantic.ValidationError as e:
        loguru.logger.error(e.json())
        return None


if __name__ == '__main__':
    with open("../../main_page_json.json", "r") as file:
        x = file.read()
    top_bar_validator(x)
    # pass
