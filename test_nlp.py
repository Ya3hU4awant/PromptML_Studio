from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "sshleifer/tiny-distilbert-base-uncased-finetuned-sst-2-english"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSequenceClassification.from_pretrained(
    model_name,
    ignore_mismatched_sizes=True
)

text = "I love this project"

inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)

scores = torch.nn.functional.softmax(outputs.logits, dim=1)

labels = ["NEGATIVE", "POSITIVE"]

result = {
    "label": labels[scores.argmax().item()],
    "score": scores.max().item()
}

print(result)
