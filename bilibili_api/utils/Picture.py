from dataclasses import dataclass
from PIL import Image
from typing import Any
import tempfile
import os
import httpx
from .Credential import Credential


@dataclass
class Picture:
    """
    (@dataclasses.dataclass)

    图片类，包含图片链接、尺寸以及下载操作。

    Args:
        height    (int)  : 高度           
        imageType (str)  : 格式，例如: png
        size      (Any)  : 尺寸           
        url       (str)  : 图片链接        
        width     (int)  : 宽度           
        content   (bytes): 图片内容       

    可以不实例化，用 `from_url` 或 `from_file` 加载图片。
    """

    height: int = -1
    imageType: str = ""
    size: Any = ""
    url: str = ""
    width: int = -1
    content: bytes = b''

    def __set_picture_meta_from_bytes(self, imgtype: str) -> None:
        tmp_dir = tempfile.gettempdir()
        img_path = os.path.join(tmp_dir, "test." + imgtype)
        with open(img_path, "wb+") as file:
            file.write(self.content)
        img = Image.open(img_path)
        self.size = img.size
        self.height = img.height
        self.width = img.width
        self.imageType = imgtype

    @staticmethod
    def from_url(url: str) -> "Picture":
        """
        加载网络图片。

        Args:
            url (str): 图片链接

        Returns:
            Picture: 加载后的图片对象
        """
        obj = Picture()
        session = httpx.Client()
        resp = session.get(url)
        obj.content = resp.read()
        obj.url = url
        obj.__set_picture_meta_from_bytes(url.split("/")[-1].split(".")[1])
        return obj

    @staticmethod
    def from_file(path: str) -> "Picture":
        """
        加载本地图片。

        Args:
            path (str): 图片地址

        Returns:
            Picture: 加载后的图片对象
        """
        obj = Picture()
        with open(path, "rb") as file:
            obj.content = file.read()
        obj.url = "file://" + path
        obj.__set_picture_meta_from_bytes(os.path.basename(path).split(".")[1])
        return obj
    
    async def upload_file(self, credential: Credential) -> "Picture":
        """
        上传图片至 B 站。

        Args:
            credential (Credential): 凭据类。

        Returns:
            Picture: `self`
        """
        from ..dynamic import upload_image
        res = await upload_image(self, credential)
        self.height = res["image_height"]
        self.width = res["image_width"]
        self.url = res["image_url"]
        return self

    def convert_format(self, new_format: str) -> "Picture":
        """
        将图片转换为另一种格式。

        Args:
            new_format (str): 新的格式。例：`png`, `ico`, `webp`. 

        Returns:
            Picture: `self`
        """
        tmp_dir = tempfile.gettempdir()
        img_path = os.path.join(tmp_dir, "test." + self.imageType)
        img = Image.open(img_path)
        new_img_path = os.path.join(tmp_dir, "test." + new_format)
        img.save(new_img_path)
        with open(new_img_path, "rb") as file:
            self.content = file.read()
        self.__set_picture_meta_from_bytes(new_format)
        return self

    async def download(self, path: str) -> "Picture":
        """
        下载图片至本地。

        Args:
            path (str): 下载地址。

        Returns:
            Picture: `self`
        """
        tmp_dir = tempfile.gettempdir()
        img_path = os.path.join(tmp_dir, "test." + self.imageType)
        img = Image.open(img_path)
        img.save(path)
        return self
