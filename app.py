from flask import Flask, render_template, request, jsonify
import sqlite3
import pickle
import numpy as np
import os
from huggingface_service import (
    translate_text, detect_language, transliterate_to_english,
    generate_health_response, detect_symptoms_with_bert
)
from speech_service import transcribe_audio

app = Flask(__name__)

# Load the ML model
model_data = None
model = None
symptoms_list = None
diseases_list = None

def load_model():
    """Load the trained ML model"""
    global model_data, model, symptoms_list, diseases_list
    model_path = 'models/health_model.pkl'
    
    if os.path.exists(model_path):
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        model = model_data['model']
        symptoms_list = model_data['symptoms']
        diseases_list = model_data['diseases']
        return True
    return False

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('database/health_app.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_disease_info(disease_name):
    """Get disease information from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM diseases WHERE name = ?
    ''', (disease_name,))
    
    disease = cursor.fetchone()
    conn.close()
    
    if disease:
        return {
            'id': disease['id'],
            'name': disease['name'],
            'description': disease['description'],
            'precautions': disease['precautions'],
            'severity_level': disease['severity_level'],
            'recommended_action': disease['recommended_action']
        }
    return None

@app.route('/')
def index():
    """Render the main page with symptoms"""
    if not symptoms_list:
        return "Model not loaded. Please run train_model.py first.", 500
    
    return render_template('index.html', symptoms=symptoms_list)

@app.route('/predict', methods=['POST'])
def predict():
    """Make disease prediction based on symptoms"""
    try:
        # Check if model is loaded
        if model is None or symptoms_list is None or diseases_list is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please restart the server.'
            }), 500
        
        data = request.get_json()
        if data is None:
            return jsonify({
                'success': False,
                'error': 'Invalid request data'
            }), 400
            
        selected_symptoms = data.get('symptoms', [])
        print(f"DEBUG: Selected symptoms: {selected_symptoms}")
        
        if not selected_symptoms:
            return jsonify({
                'success': False,
                'error': 'Please select at least one symptom'
            }), 400
        
        # Validate symptoms
        valid_symptoms = [s for s in selected_symptoms if s in symptoms_list]
        print(f"DEBUG: Valid symptoms: {valid_symptoms}")
        print(f"DEBUG: Total symptoms in model: {len(symptoms_list)}")
        
        if not valid_symptoms:
            return jsonify({
                'success': False,
                'error': f'Invalid symptoms selected. Please select from the available symptoms.'
            }), 400
        
        # Create symptom vector
        symptom_vector = [0] * len(symptoms_list)
        for symptom in valid_symptoms:
            if symptom in symptoms_list:
                idx = symptoms_list.index(symptom)
                symptom_vector[idx] = 1
        
        # Make prediction
        symptom_array = np.array([symptom_vector])
        print(f"DEBUG: Symptom array shape: {symptom_array.shape}")
        
        prediction = model.predict(symptom_array)[0]
        probabilities = model.predict_proba(symptom_array)[0]
        
        print(f"DEBUG: Prediction: {prediction}, Disease: {diseases_list[prediction]}")
        
        # Get disease name
        disease_name = diseases_list[prediction]
        confidence = float(probabilities[prediction]) * 100
        
        # Get disease info from database
        disease_info = get_disease_info(disease_name)
        
        # Get top 3 predictions with probabilities
        top_predictions = []
        sorted_indices = np.argsort(probabilities)[::-1][:3]
        for idx in sorted_indices:
            if probabilities[idx] > 0.01:  # Only include if > 1%
                top_predictions.append({
                    'disease': diseases_list[idx],
                    'probability': float(probabilities[idx]) * 100
                })
        
        return jsonify({
            'success': True,
            'prediction': {
                'disease': disease_name,
                'confidence': round(confidence, 2),
                'description': disease_info['description'] if disease_info else '',
                'precautions': disease_info['precautions'] if disease_info else '',
                'severity_level': disease_info['severity_level'] if disease_info else '',
                'recommended_action': disease_info['recommended_action'] if disease_info else ''
            },
            'all_predictions': top_predictions
        })
        
    except KeyError as e:
        print(f"KeyError in predict: {e}")
        return jsonify({
            'success': False,
            'error': f'Missing data field: {str(e)}'
        }), 400
    except ValueError as e:
        print(f"ValueError in predict: {e}")
        return jsonify({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }), 400
    except Exception as e:
        import traceback
        print(f"Error in predict: {e}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/diseases')
def get_diseases():
    """Get all diseases information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM diseases ORDER BY name')
        diseases = cursor.fetchall()
        
        result = []
        for disease in diseases:
            # Get symptoms for this disease
            cursor.execute('''
                SELECT s.name FROM symptoms s
                JOIN disease_symptoms ds ON s.id = ds.symptom_id
                WHERE ds.disease_id = ?
            ''', (disease['id'],))
            symptoms = [row['name'] for row in cursor.fetchall()]
            
            result.append({
                'id': disease['id'],
                'name': disease['name'],
                'description': disease['description'],
                'precautions': disease['precautions'],
                'severity_level': disease['severity_level'],
                'recommended_action': disease['recommended_action'],
                'symptoms': symptoms
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'diseases': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/symptoms')
def get_symptoms():
    """Get all symptoms"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM symptoms ORDER BY name')
        symptoms = cursor.fetchall()
        
        result = [{'id': s['id'], 'name': s['name']} for s in symptoms]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'symptoms': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/disease/<int:disease_id>')
def disease_detail(disease_id):
    """Render disease detail page"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get disease information
        cursor.execute('SELECT * FROM diseases WHERE id = ?', (disease_id,))
        disease = cursor.fetchone()
        
        if not disease:
            conn.close()
            return "Disease not found", 404
        
        # Get associated symptoms
        cursor.execute('''
            SELECT s.name FROM symptoms s
            JOIN disease_symptoms ds ON s.id = ds.symptom_id
            WHERE ds.disease_id = ?
            ORDER BY s.name
        ''', (disease_id,))
        symptoms = [row['name'] for row in cursor.fetchall()]
        
        conn.close()
        
        disease_data = {
            'id': disease['id'],
            'name': disease['name'],
            'description': disease['description'],
            'precautions': disease['precautions'],
            'severity_level': disease['severity_level'],
            'recommended_action': disease['recommended_action'],
            'symptoms': symptoms
        }
        
        return render_template('disease_detail.html', disease=disease_data)
        
    except Exception as e:
        return f"Error: {str(e)}", 500

# Global conversation state to track symptoms across messages
conversation_state = {}

@app.route('/chat', methods=['POST'])
def chat():
    """Process chat messages with Hugging Face AI and symptom extraction"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        language = data.get('language', 'en-US')
        history = data.get('history', [])
        
        # Get or create conversation state (using session-like approach)
        # Extract symptoms from ALL conversation history, not just current message
        all_detected_symptoms = set()
        
        # Process current message
        detected_lang = detect_language(message)
        if detected_lang in ['te', 'hi']:
            english_message = transliterate_to_english(message)
            if detect_language(english_message) != 'en':
                english_message = translate_text(message, detected_lang, 'en')
        else:
            english_message = message
        
        # Extract symptoms from current message
        current_symptoms = extract_symptoms_from_text(english_message.lower())
        all_detected_symptoms.update(current_symptoms)
        
        # Also extract symptoms from conversation history (last 5 messages)
        for msg in history[-5:]:
            if msg.get('role') == 'user':
                hist_msg = msg.get('content', '')
                hist_lang = detect_language(hist_msg)
                if hist_lang in ['te', 'hi']:
                    hist_english = transliterate_to_english(hist_msg)
                    if detect_language(hist_english) != 'en':
                        hist_english = translate_text(hist_msg, hist_lang, 'en')
                else:
                    hist_english = hist_msg
                
                hist_symptoms = extract_symptoms_from_text(hist_english.lower())
                all_detected_symptoms.update(hist_symptoms)
        
        # Convert to list for API
        detected_symptoms = list(all_detected_symptoms)
        
        # Generate AI-powered response using Hugging Face
        response = generate_health_response(message, detected_symptoms, language, history)
        
        return jsonify({
            'success': True,
            'response': response,
            'symptoms_detected': detected_symptoms,
            'language': language,
            'detected_input_language': detected_lang,
            'translated_message': english_message if detected_lang != 'en' else None
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/chatbot')
def chatbot_page():
    """Full-page chatbot interface"""
    return render_template('chatbot_page.html')

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({'status': 'ok', 'message': 'Server is working'})


@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Transcribe audio to text using AI speech recognition"""
    try:
        data = request.get_json()
        audio_base64 = data.get('audio', '')
        language = data.get('language', 'en-US')
        
        if not audio_base64:
            return jsonify({
                'success': False,
                'error': 'No audio data provided'
            }), 400
        
        # Decode base64 audio
        import base64
        try:
            # Handle data URL format (data:audio/webm;base64,....)
            if ',' in audio_base64:
                audio_data = base64.b64decode(audio_base64.split(',')[1])
            else:
                audio_data = base64.b64decode(audio_base64)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid audio data: {str(e)}'
            }), 400
        
        # Transcribe using Hugging Face Whisper (FREE)
        transcript = transcribe_audio(audio_data, language, provider='huggingface')
        
        if transcript:
            return jsonify({
                'success': True,
                'transcript': transcript,
                'language': language
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not transcribe audio. The AI model might be loading. Please wait 30 seconds and try again, or type your message.'
            }), 500
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

def extract_symptoms_from_text(text):
    """
    Extract symptoms from user message using BERT + smart heuristic matching.
    The heuristic matching handles word combinations (e.g., 'head' + 'hurt' = Headache)
    so it works flawlessly even when offline or when the HF BERT API is slow/unavailable.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM symptoms')
    all_symptoms = [row['name'] for row in cursor.fetchall()]
    conn.close()
    
    # Try BERT symptom detection
    bert_symptoms = detect_symptoms_with_bert(text, all_symptoms)
    
    # Smart Heuristic Matching
    text_lower = text.lower()
    heuristic_symptoms = []
    
    # Helper to check if any of the keywords are in the text
    def has_any(keywords):
        return any(kw in text_lower for kw in keywords)
        
    # Helper to check if combinations exist (e.g., one word from group A and one from group B)
    def has_combo(group_a, group_b):
        return any(a in text_lower for a in group_a) and any(b in text_lower for b in group_b)
        
    # Smart mappings for each of the 25 database symptoms
    symptom_rules = {
        'Fever': lambda: has_any(['fever', 'temperature', 'జ్వరం', 'జ్వరము', 'జ్వరంగా', 'बुखार', 'pyrexia', 'fevr', 'fvr', 'febrile', 'hot body', 'feeling hot']),
        'Cough': lambda: has_any(['cough', 'coughing', 'దగ్గు', 'దగ్గుగా', 'దగ్గు వస్తుంది', 'खांसी', 'dry cough', 'wet cough', 'cof', 'kof', 'khansi']),
        'Sore Throat': lambda: has_any(['sore throat', 'గొంతు నొప్పి', 'గొంతు నొప్పి', 'గొంతునొప్పి', 'गले में दर्द']) or has_combo(['throat', 'swallow'], ['pain', 'sore', 'hurt', 'irritation', 'scratchy', 'itchy']),
        'Runny Nose': lambda: has_any(['runny nose', 'nose discharge', 'नाक बहना', 'running nose', 'dripping nose', 'nasal discharge', 'blocked nose', 'stuffy nose', 'congestion', 'सर्दी', 'జలుబు', 'ముక్కు కారడం', 'ముక్కు కారటం']),
        'Sneezing': lambda: has_any(['sneezing', 'తుమ్ములు', 'తుమ్ము', 'ఈక్కుడు', 'छींक', 'sneeze', 'achoo', 'sneez']),
        'Body Aches': lambda: has_any(['body aches', 'body pain', 'శరీర నొప్పులు', 'ఒంటి నొప్పులు', 'ఒళ్ళు నొప్పులు', 'शरीर में दर्द', 'bodyache', 'aching body']) or has_combo(['body', 'limb', 'limbs'], ['pain', 'ache', 'hurt', 'sore', 'stiff']),
        'Fatigue': lambda: has_any(['fatigue', 'tired', 'అలసట', 'నీరసం', 'थकान', 'weakness', 'exhausted', 'tird', 'tyred', 'low energy', 'exhaustion', 'sleepy', 'drowsy']),
        'Headache': lambda: has_any(['headache', 'తలనొప్పి', 'తల నొప్పి', 'सिरदर्द', 'migraine', 'hedak', 'headpain', 'head ache']) or has_combo(['head', 'skull', 'forehead'], ['pain', 'ache', 'hurt', 'throbbing', 'splitting']),
        'Chills': lambda: has_any(['chills', 'shivering', 'చలి', 'వణుకు', 'జలుబు', 'ठंड लगना', 'cold sweat', 'shiver', 'rigors', 'shivered', 'feeling cold', 'सर्दी']),
        'Nausea': lambda: has_any(['nausea', 'feeling sick', 'వికారం', 'వాంతి వచ్చినట్లు', 'వాంతి వచ్చినట్టు', 'मतली', 'vomiting sensation', 'nause', 'nauzia', 'queasy', 'nauseous']),
        'Vomiting': lambda: has_any(['vomiting', 'vomit', 'వాంతులు', 'వాంతి', 'కక్కు', 'వాంతులు కావడం', 'వాంతి రావడం', 'పేచు', 'उल्टी', 'throwing up', 'vometing', 'puking', 'vomited']),
        'Diarrhea': lambda: has_any(['diarrhea', 'loose motion', 'అతిసారం', 'విరేచనాలు', 'మోషన్స్', 'दस्त', 'stomach upset', 'loose stools', 'diarhea', 'watery stool', 'runny stool']),
        'Abdominal Pain': lambda: has_any(['abdominal pain', 'కడుపు నొప్పి', 'కడుపునొప్పి', 'पेट दर्द', 'belly pain', 'tummy pain', 'abdominalpain', 'gastric pain']) or has_combo(['stomach', 'belly', 'tummy', 'abdomen', 'gut', 'guts'], ['pain', 'ache', 'hurt', 'cramp', 'cramps', 'upset', 'spasm']),
        'Loss of Taste': lambda: has_any(['loss of taste', 'no taste', 'రుచి పోవడం', 'స్वाद न आना', 'taste loss', 'tasteless', 'రుచి కోల్పోవడం', 'రుచి తెలియడం లేదు']) or has_combo(['taste'], ['loss', 'lost', 'no', 'cant', 'cannot', 'decreased']),
        'Loss of Smell': lambda: has_any(['loss of smell', 'no smell', 'వాసన పోవడం', 'गंध न आना', 'smell loss', 'వాసన కోల్పోవడం', 'వాసన తెలియడం లేదు']) or has_combo(['smell', 'scent'], ['loss', 'lost', 'no', 'cant', 'cannot', 'decreased']),
        'Shortness of Breath': lambda: has_any(['shortness of breath', 'breathing difficulty', 'శ్వాస తీసుకోవడంలో ఇబ్బంది', 'ఆయాసం', 'ఊపిరి ఆడకపోవడం', 'सांस फूलना', 'cant breathe', 'breathless', 'difficulty breathing']) or has_combo(['breath', 'breathe', 'breathing'], ['short', 'difficult', 'difficulty', 'hard', 'struggle', 'struggling', 'can\'t', 'cannot']),
        'Chest Pain': lambda: has_any(['chest pain', 'ఛాతీ నొప్పి', 'ఛాతి నొప్పి', 'छाती में दर्द', 'chestpain']) or has_combo(['chest', 'heart area', 'ribs'], ['pain', 'ache', 'hurt', 'tightness', 'pressure', 'squeezing']),
        'Sensitivity to Light': lambda: has_any(['sensitivity to light', 'photophobia', 'light sensitivity', 'కాంతి పడకపోవడం']) or has_combo(['light', 'bright'], ['sensitive', 'sensitivity', 'hurts eyes', 'eye pain']),
        'Sensitivity to Sound': lambda: has_any(['sensitivity to sound', 'phonophobia', 'sound sensitivity', 'శబ్దాలు వినలేకపోవడం']) or has_combo(['sound', 'noise', 'loud'], ['sensitive', 'sensitivity', 'hurts ears']),
        'Dizziness': lambda: has_any(['dizziness', 'lightheaded', 'తలతిరుగుడు', 'కళ్లు తిరగడం', 'కళ్ళు తిరగడం', 'चक्कर आना', 'dizzy', 'vertigo', 'spinning head', 'feeling faint', 'unsteady', 'giddiness']),
        'Rash': lambda: has_any(['rash', 'skin rash', 'దద్దులు', 'चकत्ते', 'skin spots', 'red spots', 'itchy skin', 'dermatitis', 'hives', 'spots on skin']),
        'Joint Pain': lambda: has_any(['joint pain', 'జోయింట్ నొప్పి', 'కీళ్ల నొప్పులు', 'కీళ్ళ నొప్పులు', 'जोड़ों का दर्द', 'jointpain', 'arthritis pain']) or has_combo(['joint', 'joints', 'knee', 'knees', 'elbow', 'elbows', 'wrist', 'wrists', 'shoulder', 'shoulders'], ['pain', 'ache', 'hurt', 'sore', 'stiff']),
        'Muscle Pain': lambda: has_any(['muscle pain', 'మాంసపేశీ నొప్పి', 'మాంసपेषि दर्द', 'కండరాల నొప్పులు', 'muscular pain', 'myalgia']) or has_combo(['muscle', 'muscles', 'calf', 'calves', 'thigh', 'thighs'], ['pain', 'ache', 'hurt', 'sore', 'cramp', 'cramps']),
        'Sweating': lambda: has_any(['sweating', 'excessive sweat', 'చెమట', 'చెమటలు', 'చెమట పట్టడం', 'पसीना', 'sweat', 'perspiration', 'night sweats', 'diaphoresis', 'sweaty']),
        'Loss of Appetite': lambda: has_any(['loss of appetite', 'not hungry', 'ఆకలి లేకపోవడం', 'ఆకలి వేయకపోవడం', 'ఆకలి లేదు', 'भूख न लगना', 'no appetite', 'cant eat', 'anorexia', 'poor appetite']) or has_combo(['appetite', 'hunger'], ['loss', 'lost', 'no', 'poor', 'decreased', 'cant', 'cannot'])
    }
    
    # Run the rules to extract matching symptoms
    for db_symptom, check_fn in symptom_rules.items():
        if check_fn():
            heuristic_symptoms.append(db_symptom)
            
    # Combine BERT and heuristic results (remove duplicates)
    combined_symptoms = list(set(bert_symptoms + heuristic_symptoms))
    
    print(f"DEBUG: Extracted symptoms: {combined_symptoms}")
    return combined_symptoms


def generate_chat_response(message, symptoms, language, history):
    """Generate contextual response based on user input"""
    
    # Language-specific responses
    responses = {
        'en-US': {
            'greeting': ['hello', 'hi', 'hey'],
            'greeting_response': 'Hello! I\'m your AyuMithra health assistant. How can I help you today?',
            'symptom_detected': 'I noticed you mentioned: {}. Would you like me to analyze these symptoms?',
            'multiple_symptoms': 'I see you have several symptoms. Please use our symptom checker for a comprehensive analysis.',
            'no_symptoms': 'I understand. Could you please describe your symptoms in more detail?',
            'disease_info': 'I can provide information about various diseases. What would you like to know?',
            'medical_advice': 'Please note that I\'m an AI assistant and cannot provide medical advice. Please consult a healthcare professional for proper diagnosis.',
            'thank_you': 'You\'re welcome! Take care of your health.',
            'goodbye': 'Goodbye! Stay healthy!',
            'default': 'I understand you have a health concern. Could you tell me more about your symptoms?'
        },
        'hi-IN': {
            'greeting': ['नमस्ते', 'हैलो', 'हाय'],
            'greeting_response': 'नमस्ते! मैं आपका AyuMithra स्वास्थ्य सहायक हूं। मैं आपकी कैसे मदद कर सकता हूं?',
            'symptom_detected': 'मैंने देखा कि आपने {} का उल्लेख किया है। क्या आप चाहते हैं कि मैं इन लक्षणों का विश्लेषण करूं?',
            'multiple_symptoms': 'मुझे लगता है कि आपको कई लक्षण हैं। कृपया विस्तृत विश्लेषण के लिए हमारे लक्षण जांचकर्ता का उपयोग करें।',
            'no_symptoms': 'मैं समझता हूं। क्या आप कृपया अपने लक्षणों का अधिक विस्तार से वर्णन कर सकते हैं?',
            'disease_info': 'मैं विभिन्न बीमारियों के बारे में जानकारी प्रदान कर सकता हूं। आप क्या जानना चाहेंगे?',
            'medical_advice': 'कृपया ध्यान दें कि मैं एक AI सहायक हूं और चिकित्सा सलाह नहीं दे सकता। कृपया उचित निदान के लिए एक स्वास्थ्य पेशेवर से परामर्श करें।',
            'thank_you': 'आपका स्वागत है! अपने स्वास्थ्य का ध्यान रखें।',
            'goodbye': 'अलविदा! स्वस्थ रहें!',
            'default': 'मैं समझता हूं कि आपको एक स्वास्थ्य समस्या है। क्या आप मुझे अपने लक्षणों के बारे में और बता सकते हैं?'
        },
        'te-IN': {
            'greeting': ['నమస్తే', 'హలో', 'హాయ్'],
            'greeting_response': 'నమస్తే! నేను మీ AyuMithra ఆరోగ్య సహాయకుడిని. నేను మీకు ఎలా సహాయం చేయగలను?',
            'symptom_detected': 'మీరు {} ప్రస్తావించారని నేను గమనించాను. నేను ఈ లక్షణాలను విశ్లేషించాలని మీరు కోరుకుంటున్నారా?',
            'multiple_symptoms': 'మీకు అనేక లక్షణాలు ఉన్నాయని నేను చూస్తున్నాను. సమగ్ర విశ్లేషణ కోసం దయచేసి మా లక్షణ చెక్కర్‌ను ఉపయోగించండి.',
            'no_symptoms': 'నేను అర్థం చేసుకున్నాను. దయచేసి మీ లక్షణాలను మరింత వివరంగా వివరించగలరా?',
            'disease_info': 'నేను వివిధ వ్యాధుల గురించి సమాచారం అందించగలను. మీరు ఏమి తెలుసుకోవాలనుకుంటున్నారు?',
            'medical_advice': 'దయచేసి గమనించండి, నేను AI సహాయకుడిని మరియు వైద్య సలహా ఇవ్వలేను. సరైన నిర్ధారణ కోసం దయచేసి ఒక ఆరోగ్య నిపుణుడిని సంప్రదించండి.',
            'thank_you': 'మీకు ధన్యవాదాలు! మీ ఆరోగ్యం జాగ్రత్తగా చూసుకోండి.',
            'goodbye': 'వీడ్కోలు! ఆరోగ్యంగా ఉండండి!',
            'default': 'మీకు ఆరోగ్య సమస్య ఉందని నేను అర్థం చేసుకున్నాను. మీ లక్షణాల గురించి మీరు నాకు మరింత చెప్పగలరా?'
        }
    }
    
    lang_responses = responses.get(language, responses['en-US'])
    
    # Check for greetings
    for greeting in lang_responses['greeting']:
        if greeting in message:
            return lang_responses['greeting_response']
    
    # Check for thanks
    if any(word in message for word in ['thank', 'dhanyavad', 'ధన్యవాదాలు']):
        return lang_responses['thank_you']
    
    # Check for goodbye
    if any(word in message for word in ['bye', 'alvida', 'వీడ్కోలు', 'goodbye']):
        return lang_responses['goodbye']
    
    # If symptoms detected
    if symptoms:
        if len(symptoms) >= 3:
            return lang_responses['multiple_symptoms']
        else:
            symptom_text = ', '.join(symptoms)
            return lang_responses['symptom_detected'].format(symptom_text) + ' ' + lang_responses['medical_advice']
    
    # Check for disease-related queries
    if any(word in message for word in ['disease', 'వ్యాధి', 'बीमारी', 'condition', 'disorder']):
        return lang_responses['disease_info']
    
    # Check for medical advice queries
    if any(word in message for word in ['medicine', 'doctor', 'treatment', 'cure', 'దవాఖానా', 'చికిత్స', 'दवा', 'इलाज']):
        return lang_responses['medical_advice']
    
    return lang_responses['default']

if __name__ == '__main__':
    # Initialize database if not exists
    if not os.path.exists('database/health_app.db'):
        print("Initializing database...")
        from init_database import init_database
        init_database()
    
    # Load ML model
    if load_model():
        print("[OK] Model loaded successfully")
    else:
        print("[ERROR] Model not found. Please run train_model.py first.")
        print("  Run: python train_model.py")
        exit(1)
    
    print("\nStarting AyuMithra...")
    print("Open your browser and go to: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
