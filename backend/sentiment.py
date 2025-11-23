from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_name = "cointegrated/rubert-tiny-sentiment-balanced"
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSequenceClassification.from_pretrained(model_name)

id2label = model.config.id2label

def analyze_sentiment(text: str) -> str:
    try:
        inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)

        with torch.no_grad():
            outputs = model(**inputs)
            proba = torch.sigmoid(model(**inputs).logits).cpu().numpy()[0]

        return model.config.id2label[proba.argmax()]
    except Exception as e:
        print(f"Ошибка при анализе тональности: {e}")
        return "error"

if __name__ == "__main__":
    tests = [
        "Вкусно попил кофе, персонал улыбчивый, с кайфом короче",
        "В целом не плохой кофе, но дороговато, хз",
        "Спасибо за испорченный вечер",
        "Еда вкусная, но официант хам",
        "Ни рыба ни мясо"
    ]

    print(f"Карта меток модели: {id2label}\n")

    for t in tests:
        print(f"'{t}' -> {analyze_sentiment(t)}")
