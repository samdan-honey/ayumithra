import numpy as np
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import pickle
import os

def generate_synthetic_data():
    """Generate synthetic training data for 7 diseases"""
   
    # Define symptoms (25 total)
    symptoms = [
        'Fever', 'Cough', 'Sore Throat', 'Runny Nose', 'Sneezing',
        'Body Aches', 'Fatigue', 'Headache', 'Chills', 'Nausea',
        'Vomiting', 'Diarrhea', 'Abdominal Pain', 'Loss of Taste',
        'Loss of Smell', 'Shortness of Breath', 'Chest Pain',
        'Sensitivity to Light', 'Sensitivity to Sound', 'Dizziness',
        'Rash', 'Joint Pain', 'Muscle Pain', 'Sweating', 'Loss of Appetite'
    ]
   
    # Define disease labels
    diseases = ['Flu', 'Common Cold', 'Migraine', 'Food Poisoning',
                'COVID-19', 'Dengue', 'Malaria']
   
    # Define primary symptoms for each disease (higher probability)
    disease_primary_symptoms = {
        'Flu': [0, 1, 2, 5, 6, 7, 8, 22],
        'Common Cold': [1, 2, 3, 4, 6, 7, 9],
        'Migraine': [7, 9, 17, 18, 19, 16],
        'Food Poisoning': [9, 10, 11, 12, 0, 5, 24],
        'COVID-19': [0, 1, 6, 13, 14, 15, 7, 2, 5, 22],
        'Dengue': [0, 7, 5, 20, 21, 9, 6, 12, 16],
        'Malaria': [0, 8, 23, 7, 5, 9, 10, 6, 24, 21]
    }
   
    # Define secondary symptoms (lower probability)
    disease_secondary_symptoms = {
        'Flu': [3, 4, 9, 10, 23],
        'Common Cold': [0, 5, 8, 12],
        'Migraine': [6, 10, 11],
        'Food Poisoning': [6, 7, 19, 23],
        'COVID-19': [8, 9, 10, 16, 17],
        'Dengue': [1, 2, 10, 11, 15, 22],
        'Malaria': [2, 12, 13, 15, 16, 19]
    }
   
    # Generate data
    data = []
    samples_per_disease = 75  # 75 * 7 = 525 total samples
   
    np.random.seed(42)
   
    for disease_idx, disease in enumerate(diseases):
        primary = disease_primary_symptoms[disease]
        secondary = disease_secondary_symptoms[disease]
       
        for _ in range(samples_per_disease):
            # Create empty symptom vector
            symptom_vector = [0] * len(symptoms)
           
            # Add primary symptoms (80-100% chance)
            for symptom_idx in primary:
                if np.random.random() < np.random.uniform(0.80, 1.0):
                    symptom_vector[symptom_idx] = 1
           
            # Add secondary symptoms (20-40% chance)
            for symptom_idx in secondary:
                if np.random.random() < np.random.uniform(0.20, 0.40):
                    symptom_vector[symptom_idx] = 1
           
            # Add random noise (5% chance for any other symptom)
            for i in range(len(symptoms)):
                if i not in primary and i not in secondary:
                    if np.random.random() < 0.05:
                        symptom_vector[i] = 1
           
            # Ensure at least 3 symptoms present
            if sum(symptom_vector) < 3:
                available_primary = [s for s in primary if symptom_vector[s] == 0]
                if available_primary:
                    num_to_add = min(3 - sum(symptom_vector), len(available_primary))
                    to_add = np.random.choice(available_primary, num_to_add, replace=False)
                    for idx in to_add:
                        symptom_vector[idx] = 1
           
            symptom_vector.append(disease_idx)
            data.append(symptom_vector)
   
    # Create DataFrame
    columns = symptoms + ['disease']
    df = pd.DataFrame(data, columns=columns)
   
    return df, symptoms, diseases

def train_model():
    """Train Multinomial Naive Bayes model"""
   
    print("Generating synthetic training data...")
    df, symptoms, diseases = generate_synthetic_data()
   
    print(f"✓ Generated {len(df)} training samples")
    print(f"✓ Number of symptoms: {len(symptoms)}")
    print(f"✓ Number of diseases: {len(diseases)}")
    print("\nDisease distribution:")
    print(df['disease'].value_counts().sort_index())
   
    # Split features and labels
    X = df.drop('disease', axis=1)
    y = df['disease']
   
    # Split into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
   
    print(f"\nTraining set size: {len(X_train)}")
    print(f"Testing set size: {len(X_test)}")
   
    # Train Multinomial Naive Bayes model
    print("\nTraining Multinomial Naive Bayes model...")
    model = MultinomialNB(alpha=1.0)
    model.fit(X_train, y_train)
   
    # Make predictions on test set
    y_pred = model.predict(X_test)
   
    # Evaluate model
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n✓ Model trained successfully!")
    print(f"✓ Test accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
   
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=diseases))
   
    # Save model and metadata
    os.makedirs('models', exist_ok=True)
   
    model_data = {
        'model': model,
        'symptoms': symptoms,
        'diseases': diseases
    }
   
    with open('models/health_model.pkl', 'wb') as f:
        pickle.dump(model_data, f)
   
    print("\n✓ Model saved to models/health_model.pkl")
    print("✓ Training complete!")
   
    return model, symptoms, diseases

if __name__ == '__main__':
    train_model()
