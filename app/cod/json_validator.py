import dataclasses

import pydantic
import loguru

loguru.logger.remove()
loguru.logger.add("log_validate_error.log", level="ERROR", encoding="utf-8")


# loguru.logger.remove()

# @pydantic.dataclasses.dataclass
@dataclasses.dataclass
class Product:
    name: str | None = None
    description: str | None = None
    price: float | None = None
    brand: str | None = None
    color_1: str | None = None
    color_hexCode: str | None = None
    size: dict | None = None
    hrefs_imgs_list: list | None = None


class Valid_sizes(pydantic.BaseModel):
    size: float = pydantic.Field(alias="name")
    availability: str

    # @pydantic.validator("availability")
    # def validate_availability(cls, value: str):
    #     check_tuple = ("in_stock", "coming_soon")
    #     if value in check_tuple:
    #         return value
    #     else:
    #         raise pydantic.ValidationError


class In_xmedia(pydantic.BaseModel):
    path: str
    name: str
    timestamp: str


class In_xmedia(pydantic.BaseModel):
    path: str
    name: str
    timestamp: str
    width: int


class In_colors(pydantic.BaseModel):
    hexCode: str
    name: str
    price: int
    sizes: list[Valid_sizes]
    description: str
    xmedia: list[In_xmedia]


class Detail(pydantic.BaseModel):
    colors: list[In_colors]


class Brand(pydantic.BaseModel):
    brandGroupCode: str


class In_product(pydantic.BaseModel):
    brand: Brand
    name: str
    detail: Detail


class Product_json(pydantic.BaseModel):
    product: In_product


def vallidator(raw_json: str) -> Product | None:
    try:
        json = Product_json.parse_raw(raw_json)
        json = json.dict()
        # print(json)

        # print(json["product"]["detail"]["colors"][0]["xmedia"])

        name = json["product"]["name"]
        description = json["product"]["detail"]["colors"][0]["description"]
        size = json["product"]["detail"]["colors"][0]["sizes"]
        brand = json["product"]["brand"]["brandGroupCode"]
        color_1 = json["product"]["detail"]["colors"][0]["name"]
        color_hexCode = json["product"]["detail"]["colors"][0]["hexCode"]
        price = json["product"]["detail"]["colors"][0]["price"]
        fotos = json["product"]["detail"]["colors"][0]["xmedia"]
        fotos = [
            "https://static.zara.net/photos//" + foto['path'] + f"/w/{foto['width']}/" + foto[
                "name"] + ".jpg?ts=" + foto["timestamp"]
            for foto in fotos]
        # print(fotos)
        product = Product(name=name,
                          description=description,
                          price=price,
                          brand=brand,
                          color_1=color_1,
                          color_hexCode=color_hexCode,
                          size=size,
                          hrefs_imgs_list=fotos.copy())
        return product

    except pydantic.ValidationError as e:
        loguru.logger.error(e.json())
        return None


if __name__ == '__main__':
    with open("../../json.json", "r") as file:
        raw_json_text = file.read()
    vallidator(raw_json_text)
    # pass
