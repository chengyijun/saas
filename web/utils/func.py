import hashlib
import random
import uuid
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings

default_salt = settings.SECRET_KEY


def encrypt(target: str, salt: str = default_salt) -> str:
    """
    密码加密
    :param salt:
    :param target:
    :return:
    """
    md = hashlib.md5()
    md.update(f"{target}{salt}".encode("utf-8"))
    return md.hexdigest()


def send_sms(phone: str, code: str) -> bool:
    print(f"给 {phone} 发送的验证码为 {code}")
    return True


def create_png() -> Tuple[Image.Image, str]:
    code = str(random.randint(1000, 9999))
    img = Image.new("RGBA", (100, 40), (255, 255, 255, 255))

    draw = ImageDraw.Draw(img)
    # get a font
    fnt = ImageFont.truetype("static/1.ttf", 40)
    draw.text((2, 0), code, font=fnt, fill=(0, 0, 0, 255))
    return img, code


def get_order() -> str:
    return str(uuid.uuid4())


if __name__ == '__main__':
    get_order()
