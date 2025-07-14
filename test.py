import torch
print(torch.cuda.is_available())

import whisper
import torch

print("CUDA mavjud:", torch.cuda.is_available())  # ✅ TRUE chiqishi kerak

model = whisper.load_model("base")
model = model.to("cuda")  # 👈 Majburan CUDAga o‘tkazish

print("Model qaysi device da:", next(model.parameters()).device)
