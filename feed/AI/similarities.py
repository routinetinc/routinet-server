import pickle
import numpy as np
from scipy.spatial import distance
import openai

# Initialize OpenAI API
# Note: Replace with your actual API key
openai.api_key = "APIKey"

# Softmax function
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()

# Amplify differences between similarity scores
# Amplify differences between similarity scores
def amplify_differences(similarities, scale_factor=20, power_factor=3):
    min_val = np.min(similarities)  # 最小値を取得
    adjusted_similarities = (similarities - min_val) * scale_factor  # 最小値を引いてから定数倍
    return np.power(adjusted_similarities, power_factor)  # 増幅を適用


# Load category vectors from a pickle file
with open('category_embeddings.pkl', 'rb') as f:
    category_vectors = pickle.load(f)

# Words to classify
words = """
soccer IT
"""

# Initialize dictionary to store similarities
similarities_dict = {}
total_similarities = {}

# Calculate Cosine Similarities
response = openai.Embedding.create(
    model="text-embedding-ada-002",
    input=words
)
word_vector = np.array(response['data'][0]['embedding'])

similarities = {}
for category, vector in category_vectors.items():
    actual_object = vector[0]
    if isinstance(actual_object, dict):
        embedding = actual_object['embedding']
        vector_np = np.array(embedding)
        
    similarity = 1 - distance.cosine(vector_np, word_vector)
    similarities[category] = similarity

    if category in total_similarities:
        total_similarities[category] += similarity
    else:
        total_similarities[category] = similarity

similarities_dict[words] = similarities

# Amplify differences between similarity scores
amplified_similarities = amplify_differences(np.array(list(total_similarities.values())))

# Calculate total probabilities using softmax
total_probabilities = softmax(amplified_similarities)
total_probabilities_dict = {category: prob for category, prob in zip(total_similarities.keys(), total_probabilities)}

# Print results
print("Similarities:")
print(similarities_dict)

print("Amplified Similarities:")
print(amplified_similarities)

print("Total Probabilities:")
print(total_probabilities_dict)

for key, value in total_probabilities_dict.items():
    if value > 0.05:
        print(key)
