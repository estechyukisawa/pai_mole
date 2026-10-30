import random
import time
from pathlib import Path

import cv2
import numpy as np
import rclpy
import torch
from model import make_model
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_msgs.msg import Float64

IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"
MODEL_PATH = Path(__file__).resolve().parent.parent / "mole_cnn.pt"


# 各穴の座標
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

        self.model = make_model()
        self.model.load_state_dict(torch.load(MODEL_PATH))
        self.model.eval()

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

    def find_mole_old(self):
        return detect_color(self.latest)

    def find_mole(self):
        return detect_ai(self.model, self.latest)


# 動作確認用、画像処理ベースでの決めうち
def detect_color(img):
    #    def find_mole_old(self):
    #        img = self.latest
    if img is None:
        print("no image")
        return None

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # get mole's color
    # print(hsv[160, 160])  # [ 16 146 161]
    lower = np.array([8, 80, 60])
    upper = np.array([24, 255, 255])
    # get other color
    # print(hsv[60, 60])  # [ 60 103 141]

    mask = cv2.inRange(hsv, lower, upper)
    vs, us = np.nonzero(mask)

    # debug
    #        print(cv2.imwrite(str(IMAGE_DIR / "mask.png"), mask))
    #        print(len(us))
    #        print(us.mean())
    #        print(vs.mean())

    # モグラがいない場合
    if len(us) < 50:
        return None
    # いる場合重心と一番近い穴の位置を計算
    min_distance = 1e9
    expect_pos = -1
    for i in range(9):
        i_distance = (HOLE_UV[i][0] - us.mean()) ** 2 + (HOLE_UV[i][1] - vs.mean()) ** 2
        if min_distance > i_distance:
            min_distance = i_distance
            expect_pos = i
    return expect_pos


def detect_ai(model, img):
    #    def find_mole(self):
    #        img = self.latest
    if img is None:
        print("no image")

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    rgb = cv2.resize(rgb, (64, 64))

    rgb2 = torch.from_numpy(rgb).float() / 255.0
    rgb2 = rgb2.permute(2, 0, 1)
    rgb2 = rgb2.unsqueeze(0)

    outputs = model(rgb2)
    pred = outputs.argmax(dim=1)

    #    print(pred.item())

    if pred.item() == 9:
        return None
    else:
        return pred.item()


def main():
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    rclpy.init()

    node = Whacker()

    hits = 0
    for n in range(20):
        j = random.randrange(9)
        node.wait(2)
        node.move(0.3, 0, 0)
        for i in range(9):
            node.set_mole(i, 0)
        node.wait(2)
        #        node.set_mole(j, 0.07)
        node.wait(1)
        i = node.find_mole()
        if i == j:
            hits += 1
        print("trial:" + str(n + 1) + " success:" + str(hits))
        if i is None:
            continue

        x, y = HOLE_XY[i]
        node.move(x, y, 0)
        node.wait(1)
        node.move(x, y, -0.12)
        node.wait(0.5)
        node.move(x, y, 0)
        node.wait(0.5)
        node.move(0.3, 0, 0)


if __name__ == "__main__":
    main()
