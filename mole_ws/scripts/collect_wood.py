import random
import time
from pathlib import Path

import cv2
import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float64

IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"

HOLE_UV = [
    (214, 214),
    (160, 214),
    (105, 214),
    (214, 160),
    (160, 160),
    (105, 160),
    (214, 105),
    (160, 105),
    (105, 105),
]
HOLE_XY = [
    (-0.1, -0.1),
    (-0.1, 0),
    (-0.1, 0.1),
    (0, -0.1),
    (0, 0),
    (0, 0.1),
    (0.1, -0.1),
    (0.1, 0),
    (0.1, 0.1),
]


class Whacker(Node):
    def __init__(self):
        super().__init__("whacker")
        self.subscription = self.create_subscription(
            Image,
            "/top_camera/image",
            self.on_image,
            10,
        )
        self.latest = None

        self.pub_x = self.create_publisher(Float64, "/gantry/x", 10)
        self.pub_y = self.create_publisher(Float64, "/gantry/y", 10)
        self.pub_z = self.create_publisher(Float64, "/gantry/z", 10)
        self.pub_moles = [
            self.create_publisher(Float64, f"/mole_{i}/cmd_pos", 10) for i in range(9)
        ]

    def on_image(self, msg):
        # print(msg.width, msg.height, msg.step)
        arr = np.frombuffer(msg.data, dtype=np.uint8)
        arr = arr.reshape(msg.height, msg.step)
        img = arr[:, : msg.width * 3].reshape(msg.height, msg.width, 3)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        #        print(cv2.imwrite(str(IMAGE_DIR / "cam.png"), img))
        #        print("saved")
        #        raise SystemExit
        self.latest = img

    #
    def wait(self, sec):
        now = time.time()
        while 1:
            rclpy.spin_once(self, timeout_sec=0.05)
            if time.time() - now > sec:
                break

    def move(self, x, y, z):
        self.pub_x.publish(Float64(data=float(x)))
        self.pub_y.publish(Float64(data=float(y)))
        self.pub_z.publish(Float64(data=float(z)))

    def set_mole(self, i, h):
        self.pub_moles[i].publish(Float64(data=float(h)))


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    rclpy.init()

    node = Whacker()
    node.wait(2)
    node.move(0.3, 0, 0)

    labels = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "none"]
    DATA_DIR = IMAGE_DIR / "eval_wood"

    for label in labels:
        (DATA_DIR / label).mkdir(parents=True, exist_ok=True)

    for n in range(100):
        j = random.randrange(10)
        for i in range(9):
            node.set_mole(i, 0)
        node.wait(2)
        if j < 9:
            node.set_mole(j, 0.07)
        node.wait(1)

        cv2.imwrite(str(DATA_DIR / labels[j] / f"{n:04d}.png"), node.latest)

        if n % 50 == 0:
            print(str(n) + " data collected.")


main()
