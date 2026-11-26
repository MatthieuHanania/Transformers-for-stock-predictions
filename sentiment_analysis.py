from typing import List, Tuple

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

device = "cuda:0" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(device)
labels = ["positive", "negative", "neutral"]


def get_news_sentiment(news: List[str]) -> Tuple[float, str]:
    if news:
        tokens = tokenizer(news, return_tensors="pt", padding=True, truncation=True).to(device)
        logits = model(tokens["input_ids"], attention_mask=tokens["attention_mask"])["logits"]
        probabilities = torch.nn.functional.softmax(torch.sum(logits, 0), dim=-1)
        best_idx = torch.argmax(probabilities)
        probability = probabilities[best_idx].item()
        sentiment = labels[best_idx]
        return probability, sentiment
    return 0.0, labels[-1]


if __name__ == "__main__":
    prob, sentiment = get_news_sentiment(["market is negative", "traders are positive"])
    print(f"Probability: {prob:.4f}, Sentiment: {sentiment}")
    print(f"CUDA available: {torch.cuda.is_available()}")
