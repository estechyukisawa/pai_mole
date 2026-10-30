from torch import nn


def make_model():
    model = nn.Sequential(
        nn.Conv2d(3, 16, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),  # 16 x 32 x 32
        nn.Conv2d(16, 32, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),  # 32 x 16 x 16
        nn.Conv2d(32, 64, 3, padding=1),
        nn.ReLU(),
        nn.MaxPool2d(2),  # 64 x 8 x 8
        nn.Flatten(),
        nn.Linear(64 * 8 * 8, 10),  # 10クラス
    )
    return model
