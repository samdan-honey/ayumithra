"""
Hugging Face API Service for AyuMithra
Provides multilingual NLP capabilities using free Hugging Face Inference API
"""

import requests
import os
from typing import Optional, Dict, List

# Hugging Face Inference API - No token required for basic usage
HF_API_URL = "https://api-inference.huggingface.co/models"

# Zero-shot classification model for symptom detection
SYMPTOM_DETECTION_MODEL = "facebook/bart-large-mnli"

# Hugging Face API Configuration
HF_API_TOKEN = os.getenv('HF_API_TOKEN', '')  # Optional: for higher rate limits
HF_API_URL = "https://api-inference.huggingface.co/models"

# Model IDs for different tasks
MODELS = {
    # Translation models
    'translation': {
        'te-en': 'Helsinki-NLP/opus-mt-te-en',  # Telugu to English
        'hi-en': 'Helsinki-NLP/opus-mt-hi-en',  # Hindi to English
        'en-te': 'Helsinki-NLP/opus-mt-en-te',  # English to Telugu
        'en-hi': 'Helsinki-NLP/opus-mt-en-hi',  # English to Hindi
    },
    # Multilingual understanding
    'multilingual': 'facebook/mbart-large-50-many-to-many-mmt',
    # General language understanding
    'indic': 'ai4bharat/indic-bert',
    # Text generation for health responses
    'health': 'microsoft/BioGPT-Large',
    # Fallback for simple responses
    'general': 'google/flan-t5-base'
}


def get_headers():
    """Get API headers with optional authentication"""
    headers = {"Content-Type": "application/json"}
    if HF_API_TOKEN:
        headers["Authorization"] = f"Bearer {HF_API_TOKEN}"
    return headers


def translate_text(text: str, source_lang: str, target_lang: str) -> Optional[str]:
    """
    Translate text between languages
    Supports: te (Telugu), hi (Hindi), en (English)
    """
    try:
        lang_pair = f"{source_lang}-{target_lang}"
        
        if lang_pair in MODELS['translation']:
            model_id = MODELS['translation'][lang_pair]
        else:
            # Use multilingual model for other pairs
            model_id = MODELS['multilingual']
        
        api_url = f"{HF_API_URL}/{model_id}"
        
        payload = {
            "inputs": text,
            "parameters": {
                "max_length": 512,
                "num_return_sequences": 1
            }
        }
        
        # Shorter timeout for better UX
        response = requests.post(api_url, headers=get_headers(), json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                translation = result[0].get('translation_text', result[0].get('generated_text', ''))
                if translation and translation != text:
                    return translation
        elif response.status_code == 503:
            # Model is loading, return original text
            print(f"Model {model_id} is loading, using fallback")
            return text
        
        return text
        
    except requests.exceptions.Timeout:
        print(f"Translation timeout for {lang_pair}")
        return text
    except Exception as e:
        print(f"Translation error: {e}")
        return text


def detect_language(text: str) -> str:
    """
    Detect if text contains Telugu, Hindi, or is English
    Returns: 'te', 'hi', 'en', or 'mixed'
    """
    # Telugu Unicode range
    telugu_chars = set('అఆఇఈఉఊఋఎఏఐఒఓఔంఃకఖగఘఙచఛజఝఞటఠడఢణతథదధనపఫబభమయరలవశషసహళక్షఱ')
    # Hindi Unicode range
    hindi_chars = set('अआइईउऊऋएऐओऔंःकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहक्षत्रज्ञ')
    
    has_telugu = any(char in telugu_chars for char in text)
    has_hindi = any(char in hindi_chars for char in text)
    
    if has_telugu and has_hindi:
        return 'mixed'
    elif has_telugu:
        return 'te'
    elif has_hindi:
        return 'hi'
    else:
        return 'en'


def transliterate_to_english(text: str) -> str:
    """
    Convert Romanized Telugu/Hindi (like 'jwaram', 'bukhar') to English equivalents
    """
    # Common transliteration mappings - expanded
    mappings = {
        # Telugu transliterations
        'jwaram': 'fever', 'jaram': 'fever', 'jwarem': 'fever',
        'daham': 'thirst', 'dah': 'thirst',
        'talanoppi': 'headache', 'tala': 'head', 'noppi': 'pain',
        'dagg': 'cough', 'daggu': 'cough',
        'jalan': 'burning', 'jalubu': 'cold', 'jalub': 'cold',
        'kallu': 'eyes', 'kallu nop': 'eye pain', 'kallunoppi': 'eye pain',
        'gont': 'throat', 'gontu': 'throat', 'gontu noppi': 'sore throat',
        'kadupu': 'stomach', 'kadupu noppi': 'stomach pain', 'kadupunoppi': 'stomach pain',
        'undi': 'have', 'und': 'have', 'undhi': 'have',
        'ledu': 'no', 'led': 'no',
        'naaku': 'i have', 'naku': 'i have', 'nakk': 'i have',
        'meeku': 'you have', 'mee': 'your', 'mek': 'you have',
        'emi': 'what', 'ela': 'how', 'ekkada': 'where',
        'cheppu': 'tell', 'chepp': 'tell', 'cheppandi': 'tell',
        'avutundi': 'happening', 'avutund': 'happening', 'avuthundi': 'happening',
        'vundi': 'there is', 'vund': 'there is',
        'kuda': 'also', 'kud': 'also',
        'ippudu': 'now', 'ippud': 'now',
        'roju': 'daily', 'roj': 'daily',
        'nunchi': 'from', 'nunch': 'from',
        'modal': 'started', 'modalayindi': 'started',
        'tagg': 'reduce', 'taggutundi': 'reducing',
        'perugutundi': 'increasing', 'perug': 'increasing',
        'baaga': 'very much', 'baag': 'very much',
        'takkuva': 'less', 'takk': 'less',
        'ekkuva': 'more', 'ekk': 'more',
        
        # Hindi transliterations
        'bukhar': 'fever', 'bukh': 'fever', 'bukhaar': 'fever',
        'sardi': 'cold', 'sardee': 'cold', 'sard': 'cold',
        'khansi': 'cough', 'khans': 'cough', 'khansi': 'cough',
        'sir': 'head', 'sirdard': 'headache', 'sar': 'head', 'sardard': 'headache',
        'pet': 'stomach', 'pet dard': 'stomach pain', 'petdard': 'stomach pain',
        'gale': 'throat', 'gale me dard': 'sore throat', 'galem': 'throat',
        'aankh': 'eye', 'aankhe': 'eyes', 'aankh': 'eye',
        'jalan': 'burning', 'khujli': 'itching', 'khuj': 'itching',
        'mujhe': 'i have', 'mujh': 'i have', 'muj': 'i have',
        'mera': 'my', 'meri': 'my', 'mer': 'my',
        'aapka': 'your', 'aap': 'you', 'aapke': 'your',
        'kya': 'what', 'kaise': 'how', 'kahan': 'where', 'kaha': 'where',
        'hai': 'is', 'hain': 'are', 'ho': 'are', 'tha': 'was', 'thi': 'was',
        'nahi': 'no', 'nhi': 'no', 'nai': 'no', 'nah': 'no',
        'bahut': 'very', 'zyada': 'more', 'kam': 'less', 'jyada': 'more',
        'tabiyat': 'health', 'beemar': 'sick', 'bimar': 'sick',
        'batao': 'tell', 'bata': 'tell', 'bataye': 'tell',
        'ho raha': 'happening', 'horaha': 'happening', 'horah': 'happening',
        'ho rhi': 'happening', 'horhi': 'happening',
        'din': 'days', 'dino': 'days',
        'se': 'from', 'shuru': 'started',
        'ghat': 'reduce', 'ghat raha': 'reducing',
        'badh': 'increase', 'badh raha': 'increasing',
        'abhi': 'now', 'aaj': 'today', 'kal': 'yesterday',
        'subah': 'morning', 'shaam': 'evening', 'raat': 'night',
    }
    
    text_lower = text.lower()
    
    # First try to match multi-word phrases
    for key, value in sorted(mappings.items(), key=lambda x: len(x[0]), reverse=True):
        text_lower = text_lower.replace(key, value)
    
    return text_lower


def detect_symptoms_with_bert(text: str, all_symptoms: List[str]) -> List[str]:
    """
    Use Hugging Face BERT model for zero-shot symptom classification
    This understands synonyms like 'head pain' = 'headache'
    """
    try:
        api_url = f"{HF_API_URL}/{SYMPTOM_DETECTION_MODEL}"
        
        # Prepare candidate labels (symptoms)
        candidate_labels = [s.lower() for s in all_symptoms]
        
        payload = {
            "inputs": text,
            "parameters": {
                "candidate_labels": candidate_labels,
                "multi_label": True
            }
        }
        
        response = requests.post(api_url, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract symptoms with confidence > 0.5
            detected = []
            if 'labels' in result and 'scores' in result:
                for label, score in zip(result['labels'], result['scores']):
                    if score > 0.5:  # Confidence threshold
                        # Find original case symptom name
                        for symptom in all_symptoms:
                            if symptom.lower() == label:
                                detected.append(symptom)
                                break
            
            return detected
        
        return []
        
    except Exception as e:
        print(f"BERT symptom detection error: {e}")
        return []


def detect_disease_from_context(user_message: str, history: List[dict] = None) -> Optional[str]:
    """
    Scans the current user message and the conversation history to detect 
    which disease the user is asking about or referencing.
    Supports English, Hindi, and Telugu native queries.
    """
    user_msg_lower = user_message.lower().strip()
    
    # Diseases we have in the database
    diseases = ['Flu', 'Common Cold', 'Migraine', 'Food Poisoning', 'COVID-19', 'Dengue', 'Malaria']
    
    # Check if they are explicitly asking about a disease using questioning phrases
    disease_query_phrases = [
        'what is', 'tell me about', 'info about', 'information about', 'symptoms of', 
        'precautions for', 'cure for', 'treatment for', 'explain', 'describe',
        'గురించి చెప్పు', 'గురించి వివరించు', 'వివరించు', 'గురించి',
        'के बारे में बताएं', 'के बारे में बताओ', 'क्या है', 'विवरण'
    ]
    is_explicit_query = any(phrase in user_msg_lower for phrase in disease_query_phrases)
    
    # If the user message is VERY short (1-2 words), it might just be the disease name itself
    is_just_disease_name = len(user_msg_lower.split()) <= 2
    
    # 1. First, check if the current user message explicitly mentions any disease
    for disease in diseases:
        synonyms = [disease.lower()]
        if disease == 'COVID-19':
            synonyms.extend(['covid', 'covid19', 'coronavirus', 'कोविड-19', 'कोविड', 'कोरोना', 'కోవిడ్-19', 'కోవిడ్', 'కరోనా'])
        elif disease == 'Common Cold':
            synonyms.extend(['common cold', 'सामान्य सर्दी', 'सर्दी', 'जुकाम', 'సాధారణ జలుబు', 'జలుబు'])
            # ONLY match "cold" as a disease if they are explicitly asking about it or typing only that word
            if is_explicit_query or user_msg_lower == 'cold' or 'सर्दी' in user_msg_lower or 'జలుబు' in user_msg_lower:
                synonyms.append('cold')
        elif disease == 'Flu':
            synonyms.extend(['flu', 'फ्लू', 'इन्फ्लुएंजा', 'ఇన్ఫ్లుఎంజా', 'ఫ్లూ'])
            # ONLY match "flu" as a disease if they are explicitly asking about it or typing only that word
            if is_explicit_query or is_just_disease_name or 'फ्लू' in user_msg_lower or 'ఫ్లూ' in user_msg_lower:
                synonyms.append('flu')
        elif disease == 'Migraine':
            synonyms.extend(['migraine', 'माइग्रेन', 'మైగ్రేన్', 'తీవ్ర తలనొప్పి'])
        elif disease == 'Food Poisoning':
            synonyms.extend(['food poisoning', 'फूड पॉइजनिंग', 'ఫుడ్ పాయిజనింగ్'])
        elif disease == 'Dengue':
            synonyms.extend(['dengue', 'डेंगू', 'డెంగ్యూ', 'డెంగ్యూ జ్వరం'])
        elif disease == 'Malaria':
            synonyms.extend(['malaria', 'मलेरिया', 'మలేరియా'])
                
        for syn in synonyms:
            is_ascii = all(ord(c) < 128 for c in syn)
            if is_ascii:
                import re
                match = re.search(r'\b' + re.escape(syn) + r'\b', user_msg_lower)
                if match:
                    # Ensure we only return this if it's an explicit query, just the disease name,
                    # or if it's not a list of symptoms (doesn't contain symptom words)
                    symptom_words = ['pain', 'ache', 'fever', 'cough', 'sweating', 'vomiting', 'diarrhea', 'sore', 'runny', 'chills']
                    has_symptom_words = any(w in user_msg_lower for w in symptom_words)
                    if is_explicit_query or is_just_disease_name or not has_symptom_words:
                        return disease
            else:
                if syn in user_msg_lower:
                    # Native scripts don't require word boundaries since they don't have partial word overlap bugs
                    return disease

    # 2. If the user is asking a follow-up question like "what is this disease?" or "tell me more"
    # we look backward through the history to see the most recently matched disease discussed by the assistant
    if history:
        for msg in reversed(history):
            content_lower = msg.get('content', '').lower()
            
            # Find the positions of all disease matches in this message
            found_diseases = []
            for disease in diseases:
                synonyms = [disease.lower()]
                if disease == 'COVID-19':
                    synonyms.extend(['covid', 'covid19', 'coronavirus', 'कोविड-19', 'कोविड', 'कोरोना', 'కోవిడ్-19', 'కోవిడ్', 'కరోనా'])
                elif disease == 'Common Cold':
                    synonyms.extend(['cold', 'common cold', 'सामान्य सर्दी', 'सर्दी', 'जुकाम', 'సాధారణ జలుబు', 'జలుబు'])
                elif disease == 'Flu':
                    synonyms.extend(['flu', 'फ्लू', 'इन्फ्लुएंजा', 'ఇన్ఫ్లుఎంజా', 'ఫ్లూ'])
                elif disease == 'Migraine':
                    synonyms.extend(['migraine', 'माइग्रेन', 'మైగ్రేన్', 'తీవ్ర తలనొప్పి'])
                elif disease == 'Food Poisoning':
                    synonyms.extend(['food poisoning', 'फूड पॉइजनिंग', 'ఫుడ్ పాయిజనింగ్'])
                elif disease == 'Dengue':
                    synonyms.extend(['dengue', 'डेंगू', 'డెంగ్యూ', 'డెంగ్యూ జ్వరం'])
                elif disease == 'Malaria':
                    synonyms.extend(['malaria', 'मलेरिया', 'మలేరియా'])
                    
                for syn in synonyms:
                    is_ascii = all(ord(c) < 128 for c in syn)
                    if is_ascii:
                        import re
                        match = re.search(r'\b' + re.escape(syn) + r'\b', content_lower)
                        if match:
                            found_diseases.append((match.start(), disease))
                            break # Break to avoid duplicate match of synonyms
                    else:
                        if syn in content_lower:
                            idx = content_lower.find(syn)
                            found_diseases.append((idx, disease))
                            break
            
            # If any diseases are found in this history message, return the one mentioned FIRST (top prediction!)
            if found_diseases:
                found_diseases.sort(key=lambda x: x[0])
                return found_diseases[0][1]
                        
    return None


def get_detailed_disease_info(disease_name: str, language: str = 'en-US') -> str:
    """Get detailed information about a specific disease and format it naturally"""
    try:
        # 1. Localized offline dictionary for 100% reliable translations without network
        localized_data = {
            'te-IN': {
                'Flu': {
                    'name': 'ఇన్ఫ్లుఎంజా (ఫ్లూ)',
                    'severity': 'మితమైన (Moderate)',
                    'description': 'ఇన్ఫ్లుఎంజా (ఫ్లూ) అనేది మీ శ్వాసకోశ వ్యవస్థపై దాడి చేసే ఒక వైరల్ ఇన్ఫెక్షన్.',
                    'precautions': ['విశ్రాంతి తీసుకోండి', 'మంచి నీరు త్రాగండి (హైడ్రేటెడ్ గా ఉండండి)', 'జ్వరం తగ్గే మందులు వాడండి', 'ఇతరులతో పరిచయాలను నివారించండి', 'ప్రతి సంవత్సరం ఫ్లూ వ్యాక్సిన్ తీసుకోండి'],
                    'recommendation': 'ఇంట్లోనే విశ్రాంతి తీసుకోండి, మీ లక్షణాలను గమనించండి. లక్షణాలు మరింత తీవ్రమైతే లేదా 7 రోజులకు మించి కొనసాగితే వెంటనే వైద్యుడిని సంప్రదించండి.'
                },
                'Common Cold': {
                    'name': 'సాధారణ జలుబు',
                    'severity': 'తేలికపాటి (Mild)',
                    'description': 'ఇది మీ ముక్కు మరియు గొంతు (ఎగువ శ్వాసనాళం) కి వచ్చే ఒక వైరల్ ఇన్ఫెక్షన్.',
                    'precautions': ['విశ్రాంతి తీసుకోండి', 'ద్రవ పదార్థాలు ఎక్కువగా తీసుకోండి', 'ఉప్పు నీటితో గొంతు పుక్కిలించండి', 'హ్యూమిడిఫైయర్ (ఆవిరి యంత్రాన్ని) ఉపయోగించండి', 'విటమిన్ సి తీసుకోండి'],
                    'recommendation': 'ఇంట్లోనే స్వీయ-రక్షణ తీసుకోండి. ఒకవేళ లక్షణాలు 10 రోజులకు మించి కొనసాగితే లేదా మరింత తీవ్రమైతే వైద్యుడిని సంప్రదించండి.'
                },
                'Migraine': {
                    'name': 'మైగ్రేన్ (తీవ్ర తలనొప్పి)',
                    'severity': 'మితమైన (Moderate)',
                    'description': 'ఇది వివిధ తీవ్రతలతో కూడిన తలనొప్పి, తరచుగా వికారం మరియు కాంతి, శబ్దాల పట్ల సున్నితత్వంతో కూడి ఉంటుంది.',
                    'precautions': ['చీకటిగా మరియు ప్రశాంతంగా ఉన్న గదిలో విశ్రాంతి తీసుకోండి', 'తలపైన చల్లటి గుడ్డను ఉంచండి', 'మైగ్రేన్‌ను ప్రేరేపించే విషయాలకు దూరంగా ఉండండి', 'హైడ్రేటెड గా ఉండండి', 'ఒత్తిడిని తగ్గించుకోండి'],
                    'recommendation': 'నొప్పి ప్రారంభంలోనే నొప్పి నివారణ మందులను తీసుకోండి. మైగ్రేన్ తరచుగా లేదా తీవ్రంగా ఉంటే న్యూరాలజిస్ట్‌ను సంప్రదించండి.'
                },
                'Food Poisoning': {
                    'name': 'ఫుడ్ పాయిజనింగ్',
                    'severity': 'మితమైన (Moderate)',
                    'description': 'సాధారణంగా బ్యాక్టీరియా, వైరస్‌లు లేదా పరాన్నజీవుల వల్ల కలుషితమైన ఆహారాన్ని తినడం వల్ల వచ్చే అనారోగ్యం.',
                    'precautions': ['శరీరంలో నీటి శాతం తగ్గకుండా చూసుకోండి', 'తేలికపాటి ఆహారాన్ని తీసుకోండి', 'పాల ఉత్పత్తులు మరియు కొవ్వు పదార్థాలను నివారించండి', 'तरచుగా చేతులు కడుక్కోండి'],
                    'recommendation': 'విశ్రాంతి తీసుకోండి మరియు తగినంత నీరు త్రాगండి. ఒకవేళ తీవ్రమైన డీహైడ్రేషన్, మలంలో రక్తం లేదా అధిక జ్వరం ఉంటే వెంటనే అత్యवసర చికిత్స తీసుకోండి.'
                },
                'COVID-19': {
                    'name': 'కోవిడ్-19',
                    'severity': 'తీవ్రమైనది (High)',
                    'description': 'SARS-CoV-2 వైరస్ వల్ల వచ్చే కరోనావైరస్ వ్యాధి, ఇది శ్వాసకోశ వ్యవస్థను ప్రభావితం చేస్తుంది.',
                    'precautions': ['ఐసోలేషన్‌లో ఉండండి', 'విశ్రాంతి తీసుకోండి', 'శరీరంలో నీటి శాతం తగ్గకుండా చూసుకోండి', 'ఆక్సిజన్ స్థాయిలను గమనించండి', 'వైద్యులు సూచించిన మందులు వాడండి', 'టీకాలు వేయించుకోండి'],
                    'recommendation': 'వెంటనే ఐసోలేట్ అవ్వండి. లక్షణాలను నిశితంగా గమనించండి. శ్వాస తీసుకోవడంలో ఇబ్బంది, ఛాతీ నొప్పి లేదా గందరగోళం ఏర్పడిते వెంటనే అత్యవసర వైద్య సేవలను సంప్రదించండి.'
                },
                'Dengue': {
                    'name': 'డెంగ్యూ జ్వరం',
                    'severity': 'తీవ్రమైనది (High)',
                    'description': 'దోమల ద్వారా వ్యాపించే వైరల్ ఇన్ఫెక్షన్, ఇది ఫ్లూ లాంటి లక్షణాలను కలిగిస్తుంది మరియు తీవ్రమైన డెంగ్యూగా మారే అవకాశం ఉంది.',
                    'precautions': ['విశ్రాంతి తీసుకోండి', 'ఎక్కువగా ద్రవాలు త్రాగండి', 'జ్వరానికి పారాసిటమాల్ తీసుకోండి', 'ఆస్పిరిన్ వంటి మందులను నివారించండి', 'దోమతెరలను ఉపయోగించండి'],
                    'recommendation': 'హాస్పిటలైజేషన్ అవసరం కావచ్చు. తీవ్రమైన కడుపు నొప్పి, నిరంతర వాంతులు లేదా రక్తస్రావం జరిగితే వెంటనే వైద్య సహాయం తీసుకోండి.'
                },
                'Malaria': {
                    'name': 'మలేరియా',
                    'severity': 'తీవ్రమైనది (High)',
                    'description': 'ప్లాస్మోడియం పరాన్నజీవుల వల్ల వచ్చే దోమల ద్వారా సంక్రమించే వ్యాధి.',
                    'precautions': ['మలేరియా నిరోధక మందుల పూర్తి కోర్సును పూర్తి చేయండి', 'విశ్రాంతి తీసుకోండి', 'హైడ్రేటెడ్ గా ఉండండి', 'దోమతెరలను ఉపయోగించండి', 'వ్యాధి ప్రబలంగా ఉన్న ప్రాంతాలలో నివారణ మందులు తీసుకోండి'],
                    'recommendation': 'వెంటనే వైద్య చికిత్స తీసుకోండి. మలేరియాకు డాక్టర్ సూచించిన నిరోధక మందులు మరియు వైద్య పర్యవేక్షణ అవసరం.'
                }
            },
            'hi-IN': {
                'Flu': {
                    'name': 'फ्लू (इन्फ्लूएंजा)',
                    'severity': 'मध्यम (Moderate)',
                    'description': 'इन्फ्लूएंजा एक वायरल संक्रमण है जो आपके श्वसन तंत्र पर हमला करता है।',
                    'precautions': ['आराम करें', 'शरीर में पानी की कमी न होने दें', 'बुखार कम करने की दवाएं लें', 'दूसरों के संपर्क से बचें', 'हर साल फ्लू का टीका लगवाएं'],
                    'recommendation': 'घर पर आराम करें, लक्षणों की निगरानी करें। यदि लक्षण बिगड़ते हैं या 7 दिनों से अधिक समय तक बने रहते हैं तो चिकित्सा सहायता लें।'
                },
                'Common Cold': {
                    'name': 'सामान्य सर्दी / जुकाम',
                    'severity': 'हल्का (Mild)',
                    'description': 'आपकी नाक और गले (ऊपरी श्वसन पथ) का एक वायरल संक्रमण।',
                    'precautions': ['आराम करें', 'तरल पदार्थ पिएं', 'नमक के पानी से गरारे करें', 'ह्यूमिडिफायर का उपयोग करें', 'विटामिन सी लें'],
                    'recommendation': 'घर पर स्व-देखभाल करें। यदि लक्षण 10 दिनों से अधिक समय तक रहें या बिगड़ जाएं तो डॉक्टर को दिखाएं।'
                },
                'Migraine': {
                    'name': 'माइग्रेन',
                    'severity': 'मध्यम (Moderate)',
                    'description': 'अलग-अलग तीव्रता का सिरदर्द, जो अक्सर मतली और प्रकाश तथा ध्वनि के प्रति संवेदनशीलता के साथ होता है।',
                    'precautions': ['अंधेरे शांत कमरे में आराम करें', 'ठंडी सिकाई करें', 'ट्रिगर्स से बचें', 'हाइड्रेटेड रहें', 'तनाव का प्रबंधन करें'],
                    'recommendation': 'दर्द की शुरुआत में ही दर्द निवारक दवाएं लें। यदि माइग्रेन बार-बार या गंभीर हो तो न्यूरोलॉजिस्ट से परामर्श लें।'
                },
                'Food Poisoning': {
                    'name': 'फूड पॉइजनिंग',
                    'severity': 'मध्यम (Moderate)',
                    'description': 'दूषित भोजन खाने से होने वाली बीमारी, जो आमतौर पर बैक्टीरिया, वायरस या परजीवी के कारण होती है।',
                    'precautions': ['हाइड्रेटेड रहें', 'हल्का भोजन करें', 'डेयरी और वसायुक्त खाद्य पदार्थों से बचें', 'बार-बार हाथ धोएं'],
                    'recommendation': 'आराम करें और हाइड्रेटेड रहें। गंभीर निर्जलीकरण, मल में खून आने या तेज बुखार होने पर तुरंत डॉक्टर से संपर्क करें।'
                },
                'COVID-19': {
                    'name': 'कोविड-19',
                    'severity': 'गंभीर (High)',
                    'description': 'SARS-CoV-2 वायरस के कारण होने वाली कोरोना वायरस बीमारी जो श्वसन प्रणाली को प्रभावित करती है।',
                    'precautions': ['आइसोलेट रहें', 'आराम करें', 'हाइड्रेटेड रहें', 'ऑक्सीजन स्तर की निगरानी करें', 'निर्धारित दवाएं लें', 'टीका लगवाएं'],
                    'recommendation': 'तुरंत खुद को आइसोलेट करें। लक्षणों की करीब से निगरानी करें। सांस लेने में कठिनाई, छाती में दर्द या भ्रम होने पर आपातकालीन देखभाल लें।'
                },
                'Dengue': {
                    'name': 'डेंगू',
                    'severity': 'गंभीर (High)',
                    'description': 'मच्छर जनित वायरल संक्रमण जिसके कारण फ्लू जैसी बीमारी होती है, यह गंभीर डेंगू में बदल सकता है।',
                    'precautions': ['आराम करें', 'खूब तरल पदार्थ पिएं', 'बुखार के लिए पैरासिटामोल लें', 'एस्पिरिन से बचें', 'मच्छरदानी का प्रयोग करें'],
                    'recommendation': 'अस्पताल में भर्ती होने की आवश्यकता हो सकती है। यदि पेट में तेज दर्द, लगातार उल्टी या रक्तस्राव हो तो तुरंत डॉक्टर से संपर्क करें।'
                },
                'Malaria': {
                    'name': 'मलेरिया',
                    'severity': 'गंभीर (High)',
                    'description': 'प्लास्मोडियम परजीवियों के कारण होने वाली मच्छर जनित बीमारी।',
                    'precautions': ['मलेरिया रोधी दवाओं का पूरा कोर्स लें', 'आराम करें', 'हाइड्रेटेड रहें', 'मच्छरदानी का प्रयोग करें', 'प्रभावित क्षेत्रों में निवारक दवाएं लें'],
                    'recommendation': 'तुरंत चिकित्सा उपचार लें। मलेरिया के लिए डॉक्टर के पर्चे की मलेरिया रोधी दवाओं और चिकित्सा निगरानी की आवश्यकता होती है।'
                }
            }
        }

        # 2. Check if we have a direct localized response for this disease and language
        if language in localized_data and disease_name in localized_data[language]:
            data = localized_data[language][disease_name]
            pre_str = "• " + "\n• ".join(data['precautions'])
            
            if 'te' in language:
                return (
                    f"**{data['name']}** గురించి మాట్లాడుకుందాం. ఇది సాధారణంగా **{data['severity']}** తీవ్రత కలిగిన ఆరోగ్య పరిస్థితిగా వర్గీకరించబడింది.\n\n"
                    f"{data['description']}\n\n"
                    f"**దీనిని నిర్వహించడానికి మీరు తీసుకోవలసిన కొన్ని ముఖ్యమైన జాగ్రత్తలు ఇక్కడ ఉన్నాయి:**\n"
                    f"{pre_str}\n\n"
                    f"**మేము సిఫార్సు చేసేది:** {data['recommendation']}\n\n"
                    f"దయచేసి బాగా విశ్రాంతి తీసుకోండి మరియు తగినంత మంచి నీరు త్రాగండి! మీ లక్షణాలు తీవ్రమైతే, తప్పకుండా వైద్య నిపుణుడిని సంप्रదించండి."
                )
            elif 'hi' in language:
                return (
                    f"आइए **{data['name']}** के बारे में बात करते हैं। इसे आम तौर पर **{data['severity']}** गंभीरता की स्थिति के रूप में वर्गीकृत किया गया है।\n\n"
                    f"{data['description']}\n\n"
                    f"**इसे प्रबंधित करने के लिए आपको कुछ महत्वपूर्ण सावधानियां बरतनी चाहिए:**\n"
                    f"{pre_str}\n\n"
                    f"**हमारी सिफारिश:** {data['recommendation']}\n\n"
                    f"कृपया अच्छी तरह से आराम करें और हाइड्रेटेड रहें! यदि आपके लक्षण बिगड़ते हैं, तो स्वास्थ्य पेशेवर से बात करना सुनिश्चित करें।"
                )

        # 3. Fallback to SQLite DB for English or other languages
        import sqlite3
        db_path = 'database/health_app.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM diseases WHERE name = ?
        ''', (disease_name,))
        
        disease = cursor.fetchone()
        conn.close()
        
        if disease:
            severity = disease['severity_level']
            
            explanation = (
                f"Let's talk about **{disease['name']}**. It is generally classified as a **{severity}** severity condition.\n\n"
                f"{disease['description']}\n\n"
                f"**Here are some key precautions you should take to manage it:**\n"
                f"• {disease['precautions'].replace(', ', '\n• ')}\n\n"
                f"**What we recommend:** {disease['recommended_action']}\n\n"
                f"Please rest well and stay hydrated! If your symptoms worsen, be sure to speak with a healthcare professional."
            )
            
            # Dynamic translation fallback if necessary (not usually triggered now)
            if language in ['te-IN', 'hi-IN']:
                target_lang = 'te' if 'te' in language else 'hi'
                try:
                    translated = translate_text(explanation, 'en', target_lang)
                    if translated and translated != explanation:
                        return translated
                except Exception as e:
                    print(f"Error translating detailed info: {e}")
                    
            return explanation
            
        return f"Sorry, I couldn't find detailed database information about {disease_name}."
        
    except Exception as e:
        print(f"Error getting disease info: {e}")
        return f"Sorry, I couldn't retrieve information about {disease_name}."


def generate_health_response(user_message: str, symptoms: List[str], language: str, history: List[dict] = None) -> str:
    """
    Generate AI-powered health response with a warm, conversational flow.
    Automatically handles language translation, context tracking, and DB matching.
    """
    try:
        # Translate to English if needed
        detected_lang = detect_language(user_message)
        
        if detected_lang in ['te', 'hi']:
            # First try transliteration for Romanized text
            transliterated = transliterate_to_english(user_message)
            
            # If still has native script, translate
            if detect_language(transliterated) != 'en':
                english_text = translate_text(user_message, detected_lang, 'en')
            else:
                english_text = transliterated
        else:
            english_text = user_message
            
        return generate_conversational_response(symptoms, language, english_text, history)
        
    except Exception as e:
        print(f"Conversational generation error: {e}")
        return generate_conversational_response(symptoms, language, user_message, history)


def get_disease_info_from_db(symptoms: List[str]):
    """Get disease information from database based on symptoms"""
    try:
        import sqlite3
        db_path = 'database/health_app.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if symptoms:
            cursor.execute('''
                SELECT d.id, d.name, d.description, d.precautions, d.severity_level,
                       GROUP_CONCAT(s.name) as symptoms
                FROM diseases d
                JOIN disease_symptoms ds ON d.id = ds.disease_id
                JOIN symptoms s ON ds.symptom_id = s.id
                GROUP BY d.id
            ''')
            
            diseases = cursor.fetchall()
            
            scored_diseases = []
            for disease in diseases:
                disease_symptoms = [ds.strip().lower() for ds in disease['symptoms'].split(',')]
                match_count = 0
                matched_symptoms = []
                
                for user_symptom in symptoms:
                    user_sym = user_symptom.lower().strip()
                    for ds in disease_symptoms:
                        if user_sym == ds or user_sym in ds or ds in user_sym:
                            match_count += 1
                            matched_symptoms.append(user_sym)
                            break
                
                if match_count > 0:
                    scored_diseases.append({
                        'name': disease['name'],
                        'description': disease['description'],
                        'precautions': disease['precautions'],
                        'severity': disease['severity_level'],
                        'symptoms': disease_symptoms,
                        'match_count': match_count,
                        'matched_symptoms': matched_symptoms
                    })
            
            scored_diseases.sort(key=lambda x: x['match_count'], reverse=True)
            conn.close()
            return scored_diseases[:3]
        
        conn.close()
        return []
    except Exception as e:
        print(f"Database error: {e}")
        return []


def classify_intent(user_message: str) -> dict:
    """
    Classify user intent using keyword matching and NLP
    """
    message_lower = user_message.lower()
    
    intents = {
        'greeting': ['hello', 'hi', 'hey', 'namaste', 'namaskar', 'hola', 'good morning', 'good afternoon', 'good evening', 'who are you'],
        'symptom_inquiry': ['fever', 'headache', 'pain', 'cough', 'cold', 'sick', 'not feeling', 'symptom', 'problem', 'issue', 'hurts', 'aching', 'chills', 'diarrhea', 'nausea', 'vomiting'],
        'disease_info': ['what is', 'tell me about', 'information', 'what are', 'explain', 'describe', 'disease', 'condition'],
        'precaution_request': ['precaution', 'prevention', 'avoid', 'what should i do', 'how to prevent', 'safety'],
        'treatment_request': ['treatment', 'cure', 'medicine', 'medication', 'remedy', 'how to treat', 'doctor'],
        'emergency': ['emergency', 'urgent', 'severe', 'critical', 'dying', 'unconscious', 'bleeding heavily', 'cant breathe'],
        'goodbye': ['bye', 'goodbye', 'see you', 'thanks', 'thank you', 'done'],
    }
    
    intent_scores = {}
    for intent, keywords in intents.items():
        score = sum(1 for keyword in keywords if keyword in message_lower)
        intent_scores[intent] = score
    
    symptom_keywords = ['have', 'has', 'had', 'feeling', 'experiencing', 'suffering', 'pain', 'ache', 'fever', 'cough', 'cold', 'headache', 'chills', 'diarrhea', 'nausea', 'vomiting', 'tired', 'fatigue', 'sore', 'throat', 'chest', 'stomach']
    has_symptom_words = any(kw in message_lower for kw in symptom_keywords)
    
    if has_symptom_words and intent_scores['symptom_inquiry'] > 0:
        best_intent = 'symptom_inquiry'
        best_score = intent_scores['symptom_inquiry']
    else:
        best_intent = max(intent_scores, key=intent_scores.get)
        best_score = intent_scores[best_intent]
    
    entities = {
        'symptoms': [],
        'disease': None,
        'body_part': None,
        'duration': None,
        'severity': None
    }
    
    common_symptoms = ['fever', 'headache', 'cough', 'cold', 'pain', 'nausea', 'vomiting', 'diarrhea', 'fatigue', 'tired', 'weakness', 'chills', 'sore throat', 'runny nose', 'sneezing', 'body aches', 'muscle pain', 'joint pain', 'chest pain', 'shortness of breath', 'loss of taste', 'loss of smell', 'dizziness', 'rash', 'sweating', 'loss of appetite']
    for symptom in common_symptoms:
        if symptom in message_lower:
            entities['symptoms'].append(symptom)
    
    body_parts = ['head', 'stomach', 'chest', 'back', 'throat', 'nose', 'eyes', 'ears', 'legs', 'arms', 'joints', 'muscles']
    for part in body_parts:
        if part in message_lower:
            entities['body_part'] = part
            break
            
    return {
        'intent': best_intent if best_score > 0 else 'unknown',
        'confidence': min(best_score / 2, 1.0),
        'entities': entities,
        'all_scores': intent_scores
    }


def run_symptom_analyzer(symptoms: List[str]) -> dict:
    """
    Run the ML symptom analyzer on detected symptoms
    """
    try:
        import sqlite3
        import pickle
        import numpy as np
        
        model_path = 'models/health_model.pkl'
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        model = model_data['model']
        symptoms_list = model_data['symptoms']
        diseases_list = model_data['diseases']
        
        symptom_vector = [0] * len(symptoms_list)
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            for i, s in enumerate(symptoms_list):
                if symptom_lower in s.lower() or s.lower() in symptom_lower:
                    symptom_vector[i] = 1
                    break
        
        symptom_array = np.array([symptom_vector])
        prediction = model.predict(symptom_array)[0]
        probabilities = model.predict_proba(symptom_array)[0]
        
        top_predictions = []
        sorted_indices = np.argsort(probabilities)[::-1][:3]
        
        db_path = 'database/health_app.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        for idx in sorted_indices:
            if probabilities[idx] > 0.01:
                disease_name = diseases_list[idx]
                confidence = float(probabilities[idx]) * 100
                
                cursor.execute('''
                    SELECT description, precautions, recommended_action, severity_level
                    FROM diseases WHERE name = ?
                ''', (disease_name,))
                disease_info = cursor.fetchone()
                
                top_predictions.append({
                    'name': disease_name,
                    'confidence': confidence,
                    'description': disease_info['description'] if disease_info else '',
                    'precautions': disease_info['precautions'] if disease_info else '',
                    'recommended_action': disease_info['recommended_action'] if disease_info else '',
                    'severity': disease_info['severity_level'] if disease_info else 'Unknown'
                })
        
        conn.close()
        
        if top_predictions:
            return {
                'top_prediction': top_predictions[0],
                'all_predictions': top_predictions
            }
        return None
    except Exception as e:
        print(f"Analyzer error: {e}")
        return None


def similarity_score(s1: str, s2: str) -> float:
    """Simple similarity score between two strings"""
    if s1 == s2:
        return 1.0
    if s1 in s2 or s2 in s1:
        return 0.8
    words1 = set(s1.split())
    words2 = set(s2.split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union)


def get_symptom_translation(symptom_name: str, language: str) -> str:
    """Translate symptom and disease names to local language"""
    symptom_normalized = symptom_name.lower().strip()
    
    translations = {
        'te-IN': {
            'fever': 'జ్వరం',
            'cough': 'దగ్గు',
            'sore throat': 'గొంతు నొప్పి',
            'runny nose': 'జలుబు',
            'sneezing': 'తుమ్ములు',
            'body aches': 'శరీర నొప్పులు',
            'fatigue': 'అలసట',
            'headache': 'తలనొప్పి',
            'chills': 'వణుకు',
            'nausea': 'వికారం',
            'vomiting': 'వాంతులు',
            'diarrhea': 'అతిసారం',
            'abdominal pain': 'కడుపు నొప్పి',
            'loss of taste': 'రుచి కోల్పోవడం',
            'loss of smell': 'వాసన కోల్పోవడం',
            'shortness of breath': 'శ్వాస తీసుకోవడంలో ఇబ్బంది',
            'chest pain': 'ఛాతీ నొప్పి',
            'sensitivity to light': 'కాంతికి సున్నితత్వం',
            'sensitivity to sound': 'శబ్దానికి సున్నితత్వం',
            'dizziness': 'కళ్లు తిరగడం',
            'rash': 'దద్దుర్లు',
            'joint pain': 'కీళ్ల నొప్పులు',
            'muscle pain': 'కండరాల నొప్పులు',
            'sweating': 'చెమటలు పట్టడం',
            'loss of appetite': 'ఆకలి లేకపోవడం',
            
            # Diseases
            'common cold': 'సాధారణ జలుబు',
            'flu': 'ఇన్ఫ్లుఎంజా (ఫ్లూ)',
            'migraine': 'మైగ్రేన్ (తీవ్ర తలనొప్పి)',
            'food poisoning': 'ఫుడ్ పాయిజనింగ్',
            'covid-19': 'కోవిడ్-19',
            'dengue': 'డెంగ్యూ జ్వరం',
            'malaria': 'మలేరియా'
        },
        'hi-IN': {
            'fever': 'बुखार',
            'cough': 'खांसी',
            'sore throat': 'गले में दर्द',
            'runny nose': 'नाक बहना',
            'sneezing': 'छींक',
            'body aches': 'शरीर में दर्द',
            'fatigue': 'थकान',
            'headache': 'सिरदर्द',
            'chills': 'ठंड लगना',
            'nausea': 'मतली',
            'vomiting': 'उल्टी',
            'diarrhea': 'दस्त',
            'abdominal pain': 'पेट दर्द',
            'loss of taste': 'स्वाद न आना',
            'loss of smell': 'गंध न आना',
            'shortness of breath': 'सांस फूलना',
            'chest pain': 'छाती में दर्द',
            'sensitivity to light': 'प्रकाश के प्रति संवेदनशीलता',
            'sensitivity to sound': 'ध्वनि के प्रति संवेदनशीलता',
            'dizziness': 'चक्कर आना',
            'rash': 'चकत्ते',
            'joint pain': 'जोड़ों का दर्द',
            'muscle pain': 'मांसपेशियों में दर्द',
            'sweating': 'पसीना आना',
            'loss of appetite': 'भूख न लगना',
            
            # Diseases
            'common cold': 'सामान्य सर्दी',
            'flu': 'फ्लू',
            'migraine': 'माइग्रेन',
            'food poisoning': 'फूड पॉइजनिंग',
            'covid-19': 'कोविड-19',
            'dengue': 'डेंगू',
            'malaria': 'मलेरिया'
        }
    }
    
    if language in translations:
        result = translations[language].get(symptom_normalized, None)
        if result:
            return result
        for key, value in translations[language].items():
            if key in symptom_normalized or symptom_normalized in key:
                return value
                
    return symptom_name


def generate_conversational_response(symptoms: List[str], language: str, user_message: str = "", history: List[dict] = None) -> str:
    """
    Generate an empathetic, contextually aware, warm conversational response.
    Translates dynamically and integrates direct database health advice.
    """
    intent_data = classify_intent(user_message)
    intent = intent_data['intent']
    entities = intent_data['entities']
    
    # 1. Check if the user is asking about a specific disease (e.g. follow-up context)
    target_disease = detect_disease_from_context(user_message, history)
    
    # Check if the user is reporting a new symptom in their message
    has_new_symptoms = len(entities['symptoms']) > 0
    
    # If a disease is found, they are NOT reporting new symptoms, and they ask for details:
    if target_disease and not has_new_symptoms and (intent in ['disease_info', 'treatment_request', 'precaution_request'] or len(user_message.split()) <= 4):
        return get_detailed_disease_info(target_disease, language)
        
    # 2. Empathy Greetings
    responses = {
        'en-US': {
            'greeting': ["Hello! I'm AyuMithra, your virtual health companion. How are you feeling today?",
                         "Hi there! I'm here to help with your health questions. Tell me what symptoms you are experiencing.",
                         "Welcome! I'm AyuMithra. Tell me about your health concerns and I'll do my best to assist you."],
            'emergency': "🚨 This sounds like it could be a serious medical concern. Please call emergency services (108 in India) or go to the nearest clinic/hospital immediately. Do not wait for online advice.",
            'goodbye': "Take care! Be sure to rest, stay hydrated, and check in if you need anything else. Stay healthy! 🏥",
            'general_chat': "I'm AyuMithra, your AI health assistant. I can help analyze your symptoms, give info about common conditions, and share helpful precautions. What concerns do you have today?",
            'no_symptoms': "I'm here to help! Could you describe your symptoms? For example: fever, cough, headache, or body pain.",
            'symptom_intro': "Okay, I see you are experiencing **{symptoms}**. Let me run this through our analyzer.\n\nBased on your symptoms, here are the most likely possibilities:",
            'symptom_instruction': "\n\n💡 Would you like to know more details or precautions about any of these? Just type **'tell me about [disease name]'** or **'what is [disease name]'** and I will explain it naturally!",
            'one_symptom': "You mentioned having **{symptom}**. This is a common symptom but can be linked to several conditions. Do you have any other symptoms, such as fever, fatigue, or cough? Sharing more details helps me give a better estimate!"
        },
        'hi-IN': {
            'greeting': ["नमस्ते! मैं AyuMithra हूं, आपका स्वास्थ्य सहायक। आज आप कैसा महसूस कर रहे हैं?",
                         "नमस्ते! मैं आपके स्वास्थ्य संबंधी सवालों में मदद करने के लिए यहाँ हूँ। मुझे बताएं कि आप क्या लक्षण महसूस कर रहे हैं।",
                         "स्वागत है! मैं AyuMithra हूँ। अपनी स्वास्थ्य समस्याओं के बारे में बताएं और मैं आपकी पूरी मदद करूँगा।"],
            'emergency': "🚨 यह एक गंभीर चिकित्सा समस्या लग रही है। कृपया तुरंत आपातकालीन सेवाओं (भारत में 108) को कॉल करें या निकटतम अस्पताल जाएं। ऑनलाइन सलाह का इंतजार न करें।",
            'goodbye': "अपना ख्याल रखें! आराम करें, खूब पानी पिएं, और जरूरत पड़ने पर मुझसे बात करें। स्वस्थ रहें! 🏥",
            'general_chat': "मैं AyuMithra हूँ, आपका AI स्वास्थ्य सहायक। मैं आपके लक्षणों का विश्लेषण करने, सामान्य बीमारियों की जानकारी देने और सावधानियां बताने में मदद कर सकता हूँ।",
            'no_symptoms': "मैं मदद के लिए यहाँ हूँ! क्या आप मुझे बता सकते हैं कि आप कौन से लक्षण महसूस कर रहे हैं? जैसे: बुखार, खांसी, सिरदर्द या बदन दर्द।",
            'symptom_intro': "ठीक है, मैं देखता हूँ कि आपको **{symptoms}** की समस्या है। चलिए इसका विश्लेषण करते हैं।\n\nआपके लक्षणों के आधार पर, सबसे संभावित स्थितियां इस प्रकार हैं:",
            'symptom_instruction': "\n\n💡 क्या आप इनमें से किसी भी बीमारी के बारे में अधिक विवरण या सावधानियां जानना चाहते हैं? बस **'मुझे [बीमारी का नाम] के बारे में बताएं'** टाइप करें और मैं इसे समझाऊंगा!",
            'one_symptom': "आपने **{symptom}** का उल्लेख किया। यह एक सामान्य लक्षण है लेकिन कई स्थितियों से जुड़ा हो सकता है। क्या आपको कोई अन्य लक्षण हैं, जैसे बुखार, थकान या खांसी? और जानकारी देने से बेहतर विश्लेषण में मदद मिलेगी!"
        },
        'te-IN': {
            'greeting': ["నమస్తే! నేను AyuMithra, మీ ఆరోగ్య సహాయకుడిని. ఈ రోజు మీ ఆరోగ్యం ఎలా ఉంది?",
                         "హాయ్! మీ ఆరోగ్య ప్రశ్నలతో సహాయం చేయడానికి నేను ఇక్కడ ఉన్నాను. మీరు ఏ లక్షణాలను అనుభవిస్తున్నారో నాకు చెప్పండి.",
                         "స్వాగతం! నేను AyuMithra. మీ ఆరోగ్య సమస్యల గురించి నాకు చెప్పండి, నేను సహాయం చేయడానికి నా వంతు కృషి చేస్తాను."],
            'emergency': "🚨 ఇది తీవ్రమైన వైద్య అత్యవసర పరిస్థితి కావచ్చు. దయచేసి వెంటనే అత్యవసర సేవలను (భారతదేశంలో 108) సంప్రదించండి లేదా సమీపంలోని ఆసుపత్రికి వెళ్ళండి. ఆన్‌లైన్ సలహా కోసం వేచి ఉండకండి.",
            'goodbye': "జాగ్రత్త! బాగా విశ్రాంతి తీసుకోండి, మంచి నీరు త్రాగండి మరియు ఆరోగ్యంగా ఉండండి! 🏥",
            'general_chat': "నేను AyuMithra, మీ AI ఆరోగ్య సహాయకుడిని. నేను మీ లక్షణాలను విశ్లేషించడంలో, వ్యాధుల సమాచారాన్ని మరియు జాగ్రత్తలను అందించడంలో సహాయపడగలను.",
            'no_symptoms': "నేను సహాయం చేయడానికి ఇక్కడ ఉన్నాను! మీకు ఉన్న లక్షణాలను వివరించగలరా? ఉదాహరణకు: జ్వరం, దగ్గు, తలనొప్పి లేదా ఒంటి నొప్పులు.",
            'symptom_intro': "సరే, మీరు **{symptoms}** అనుభవిస్తున్నట్లు నేను గమనించాను. మా విశ్లేషకం ద్వారా దీనిని పరిశీలిద్దాం.\n\nమీ లక్షణాల ఆధారంగా, అత్యంత సంభవనీయమైన పరిస్థితులు ఇక్కడ ఉన్నాయి:",
            'symptom_instruction': "\n\n💡 వీటిలో దేని గురించైనా మరింత సమాచారం లేదా జాగ్రత్తలు తెలుసుకోవాలనుకుంటున్నారా? కేవలం **'[వ్యాధి పేరు] గురించి చెప్పు'** అని టైప్ చేయండి, నేను వివరంగా వివరిస్తాను!",
            'one_symptom': "మీరు **{symptom}** గురించి చెప్పారు. ఇది సాధారణ లక్షణమే అయినప్పటికీ చాలా వ్యాధులకు సంకేతం కావచ్చు. మీకు జ్వరం, అలసట లేదా దగ్గు వంటి ఇతర లక్షణాలు కూడా ఉన్నాయా? మరిన్ని వివరాలు చెబితే నేను మరింత ఖచ్చితంగా చెప్పగలను!"
        }
    }
    
    lang_res = responses.get(language, responses['en-US'])
    
    # 3. Handle basic intents
    if intent == 'greeting':
        import random
        return random.choice(lang_res['greeting'])
        
    elif intent == 'emergency':
        return lang_res['emergency']
        
    elif intent == 'goodbye':
        return lang_res['goodbye']
        
    elif intent == 'general_chat':
        return lang_res['general_chat']
        
    # 4. Handle symptoms analysis
    all_symptoms = list(set([s.lower().strip() for s in symptoms + entities['symptoms']]))
    
    if all_symptoms:
        # If user only mentions ONE symptom, gently ask for more details to make it conversational
        if len(all_symptoms) == 1:
            sym_trans = get_symptom_translation(all_symptoms[0], language)
            return lang_res['one_symptom'].format(symptom=sym_trans)
            
        analysis_result = run_symptom_analyzer(all_symptoms)
        if analysis_result:
            all_preds = analysis_result['all_predictions']
            
            # Translate input symptoms for the user confirmation
            translated_symptoms = [get_symptom_translation(s.strip(), language) for s in all_symptoms]
            symptom_text = ', '.join(translated_symptoms)
            
            # Intro
            intro = lang_res['symptom_intro'].format(symptoms=symptom_text)
            
            # Predictions list
            preds_lines = []
            for i, pred in enumerate(all_preds[:3], 1):
                trans_disease = get_symptom_translation(pred['name'], language)
                preds_lines.append(f"\n{i}. **{trans_disease}** ({pred['confidence']:.1f}% match)")
                
            # Add instruction
            full_response = intro + "".join(preds_lines) + lang_res['symptom_instruction']
            return full_response
            
        else:
            # Fallback when model yields no high probabilities
            translated_symptoms = [get_symptom_translation(s.strip(), language) for s in all_symptoms]
            symptom_text = ', '.join(translated_symptoms)
            if language == 'te-IN':
                return f"నేను మీ లక్షణాలు (**{symptom_text}**) చూశాను. అయితే నా వద్ద ఖచ్చితంగా సరిపోయే వ్యాధి దొరకలేదు. దయచేసి విశ్రాంతి తీసుకోండి మరియు లక్షణాలు తీవ్రమైతే వైద్యుడిని సంప్రదించండి."
            elif language == 'hi-IN':
                return f"मैंने आपके लक्षण (**{symptom_text}**) देखे हैं। लेकिन मुझे कोई सटीक मिलान नहीं मिला। कृपया आराम करें, और यदि लक्षण बिगड़ते हैं, तो डॉक्टर से संपर्क करें।"
            else:
                return f"I noted your symptoms (**{symptom_text}**). However, I couldn't find an exact matching condition in my database. Please rest up, monitor your symptoms, and consult a doctor if they persist."
                
    # No symptoms found
    if intent == 'precaution_request':
        if language == 'te-IN':
            return "నేను జాగ్రత్తలు చెప్పగలను, కానీ మీకు ఏ లక్షణాలు లేదా ఏ వ్యాధి గురించిన సమాచారం కావాలో చెబితే బాగుంటుంది."
        elif language == 'hi-IN':
            return "मैं सावधानियां बता सकता हूं, लेकिन मुझे यह जानने की आवश्यकता है कि आपको क्या लक्षण या बीमारी है।"
        else:
            return "I'd be happy to share precautions! Could you let me know what symptoms or disease you're concerned about?"
            
    elif intent == 'treatment_request':
        if language == 'te-IN':
            return "నేను సాధారణ వైద్య సమాచారం అందించగలను, కానీ ముందుగా మీ లక్షణాలు ఏంటో వివరించండి."
        elif language == 'hi-IN':
            return "मैं सामान्य उपचार जानकारी दे सकता हूँ, लेकिन पहले मुझे आपके लक्षणों को समझने की आवश्यकता है।"
        else:
            return "I can provide general treatment information, but first I need to understand your symptoms. What are you experiencing?"
            
    return lang_res['no_symptoms']


# Simple test function
if __name__ == '__main__':
    print("Multilingual Conversational Health Service ready!")
    print("Testing Translation...")
    result = translate_text("నాకు జ్వరం ఉంది", "te", "en")
    print(f"Telugu: 'నాకు జ్వరం ఉంది' -> English: {result}")
    
    print("\nTesting language detection...")
    print(f"'నాకు జ్వరం' is: {detect_language('నాకు జ్వరం')}")
    print(f"'मुझे बुखार है' is: {detect_language('मुझे बुखार है')}")
    print(f"'I have fever' is: {detect_language('I have fever')}")
