API_URL = "https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english"

def analyze_prompt(user_prompt):
    response = requests.post(API_URL, json={"inputs": user_prompt})
    return response.json()

if __name__ == "__main__":
    text = input("Enter your prompt: ")
    result = analyze_prompt(text)
    print(result)


def analyze_prompt(prompt):
    prompt = prompt.lower()

    if "predict" in prompt:
        return "Prediction Task"
    elif "classify" in prompt:
        return "Classification Task"
    elif "cluster" in prompt:
        return "Clustering Task"
    else:
        return "Unknown Task"