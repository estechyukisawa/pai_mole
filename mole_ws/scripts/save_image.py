from pathlib import Path

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image

IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"


class ImageSaver(Node):
    def __init__(self):
        super().__init__("image_saver")
        self.subscription = self.create_subscription(
            Image,
            "/top_camera/image",
            self.on_image,
            10,
        )

    def on_image(self, msg):
        # print(msg.width, msg.height, msg.step)
        arr = np.frombuffer(msg.data, dtype=np.uint8)
        arr = arr.reshape(msg.height, msg.step)
        img = arr[:, : msg.width * 3].reshape(msg.height, msg.width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        print(cv2.imwrite(str(IMAGE_DIR / "cam.png"), img))
        print("saved")
        raise SystemExit


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    rclpy.init()
    node = ImageSaver()
    rclpy.spin(node)


main()
