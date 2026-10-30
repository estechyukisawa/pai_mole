from pathlib import Path

import torch
from model import make_model
from torch import nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, transforms

DATA_DIR = Path(__file__).resolve().parent.parent / "images" / "dataset"
MODEL_PATH = Path(__file__).resolve().parent.parent / "mole_cnn.pt"

# ---- 1. データの読み込み ----
transform = transforms.Compose(
    [
        transforms.Resize((64, 64)),  # 64x64 に縮小
        transforms.ToTensor(),  # 0〜1 の数字のテンソルにする
    ]
)
dataset = datasets.ImageFolder(str(DATA_DIR), transform=transform)
print(dataset.classes)  # ['0', '1', ..., '8', 'none'] と出るはず

# ---- 2. 学習用と検証用に分ける（8:2） ----
per_val = 0.2
n_val = int(len(dataset) * per_val)
n_train = len(dataset) - n_val
train_set, val_set = random_split(
    dataset, [n_train, n_val], generator=torch.Generator().manual_seed(0)
)
train_loader = DataLoader(train_set, batch_size=32, shuffle=True)
val_loader = DataLoader(val_set, batch_size=32)

# ---- 3. モデル（CNN） ----
# model.py へ移動
model = make_model()

# ---- 4. 学習 ----
loss_fn = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

for epoch in range(10):
    model.train()
    for images, labels in train_loader:
        outputs = model(images)
        loss = loss_fn(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # 検証用データで正解率を測る
    model.eval()
    correct = 0
    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images)
            pred = outputs.argmax(dim=1)  # 一番点数の高いクラス
            correct += (pred == labels).sum().item()
    print(f"epoch {epoch + 1}: loss {loss.item():.3f}, val acc {correct / n_val:.3f}")

# ---- 5. 保存 ----
torch.save(model.state_dict(), str(MODEL_PATH))
print("saved", MODEL_PATH)
