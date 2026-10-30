from pathlib import Path

import cv2
import torch
from model import make_model
from whack_ai import MODEL_PATH, detect_ai, detect_color

IMAGE_DIR = Path(__file__).resolve().parent.parent / "images"
LABELS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "none"]

# モデルを読み込む
model = make_model()
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

for condition in ["eval_normal", "eval_wood"]:
    total = 0
    ok_color = 0
    ok_ai = 0
    for label in LABELS:
        # 正解：none なら None、それ以外なら番号（整数）
        answer = None if label == "none" else int(label)

        for path in (IMAGE_DIR / condition / label).glob("*.png"):
            img = cv2.imread(str(path))
            total += 1
            if detect_color(img) == answer:
                ok_color += 1
            if detect_ai(model, img) == answer:
                ok_ai += 1

    print(f"{condition}: color {ok_color}/{total}, AI {ok_ai}/{total}")
