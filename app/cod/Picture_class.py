import time
# import app.config as config
import requests as req
import loguru
import fake_useragent


# loguru.logger.remove()
# loguru.logger.add(config.log_picture_name, level="ERROR")


class Picture:
    def __init__(self, url):
        self.url = url

    def load_picture(self) -> True | False:
        user_agent = fake_useragent.UserAgent()
        self.response = req.get(self.url, headers={"user-agent": str(user_agent)}, stream=True)
        if self.response.ok:
            return True
        else:
            return False

    def save_picture(self, path_name: str):
        if self.response.ok:
            with open(path_name, "wb") as file:
                for chunk in self.response.iter_content(chunk_size=500000):
                    if chunk:
                        file.write(chunk)
        else:
            loguru.logger.error(f"url = {self.url}, path_name = {path_name}")


if __name__ == '__main__':
    # x = Picture(
    #     "https://static.zara.net/photos///2022/I/1/1/p/2107/010/040/2/w/333/2107010040_15_1_1.jpg?ts=1667384988296")
    # x.upload_picture()
    # x.save_picture("../1.jpg")
   pass