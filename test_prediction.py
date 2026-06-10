import pickle
import numpy as np

# Load model
model_data = pickle.load(open('models/health_model.pkl', 'rb'))
model = model_data['model']
symptoms_list = model_data['symptoms']
diseases_list = model_data['diseases']

# Test symptoms: Dizziness, Fatigue
test_symptoms = ['Dizziness', 'Fatigue']

# Create symptom vector
symptom_vector = [0] * len(symptoms_list)
for symptom in test_symptoms:
    for i, s in enumerate(symptoms_list):
        if symptom.lower() in s.lower() or s.lower() in symptom.lower():
            symptom_vector[i] = 1
            print(f"✓ Matched: {symptom} -> {s}")
            break

# Make prediction
result = model.predict([symptom_vector])[0]
probs = model.predict_proba([symptom_vector])[0]

# Show results
print(f"\n{'='*50}")
print(f"Symptoms: {', '.join(test_symptoms)}")
print(f"{'='*50}")
print(f"\nTop Prediction: {diseases_list[result]}")
print(f"Confidence: {max(probs)*100:.1f}%")

print(f"\nTop 3 Predictions:")
top3 = np.argsort(probs)[::-1][:3]
for i, idx in enumerate(top3):
    print(f"{i+1}. {diseases_list[idx]}: {probs[idx]*100:.1f}%")

print(f"\n{'='*50}")
