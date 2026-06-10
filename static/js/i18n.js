// AyuMithra Internationalization (i18n) - Language Switcher

const translations = {
    en: {
        // Navigation
        symptom_checker: "Symptom Checker",
        diseases: "Diseases",
        search_diseases: "Search diseases...",
        
        // Header
        welcome_title: "AyuMithra",
        welcome_subtitle: "Care that speaks your language",
        
        // Symptom Section
        select_symptoms: "Select Your Symptoms",
        select_symptoms_desc: "Check all the symptoms you're experiencing for an accurate analysis",
        analyze_symptoms: "Analyze Symptoms",
        clear_all: "Clear All",
        ai_chatbot: "AI Chatbot",
        
        // Results
        analysis_results: "Analysis Results",
        predicted_condition: "Predicted Condition",
        confidence: "Confidence",
        description: "Description",
        precautions: "Precautions",
        severity: "Severity",
        recommended_action: "Recommended Action",
        alternative_possibilities: "Alternative Possibilities",
        medical_disclaimer: "Medical Disclaimer",
        disclaimer_text: "This tool provides general information only and is not a substitute for professional medical advice. Always consult a healthcare provider for proper diagnosis and treatment.",
        
        // Severity levels
        mild: "Mild",
        moderate: "Moderate",
        high: "High",
        
        // Actions
        consult_doctor: "Consult Doctor",
        rest_home: "Rest at Home",
        monitor: "Monitor Symptoms",
        seek_attention: "Seek Medical Attention",
        
        // Chatbot
        chat_title: "AyuMithra Assistant",
        chat_placeholder: "Type your health question...",
        chat_listening: "Listening...",
        chat_transcribing: "Transcribing...",
        chat_welcome: "Hello! I'm your AyuMithra health assistant. I can help you with health-related questions, understanding symptoms, and providing disease information. You can type or speak to me in English, Hindi, or Telugu!",
        
        // Info Cards
        how_it_works: "How It Works",
        how_it_works_desc: "Select your symptoms from the list above and click 'Analyze Symptoms' to get a prediction.",
        accuracy: "Accuracy",
        accuracy_desc: "Our ML model is trained on thousands of cases with 97%+ accuracy for common conditions.",
        privacy: "Privacy First",
        privacy_desc: "Your health data stays on your device. We don't store any personal information.",
        
        // Buttons
        learn_more: "Learn More",
        get_started: "Get Started",
        back: "Back",
        
        // Disease Detail
        disease_info: "Disease Information",
        associated_symptoms: "Associated Symptoms",
        related_diseases: "Related Diseases",
        check_symptoms: "Check Symptoms for This Disease"
    },
    
    hi: {
        // Navigation
        symptom_checker: "लक्षण जांच",
        diseases: "बीमारियां",
        search_diseases: "बीमारियां खोजें...",
        
        // Header
        welcome_title: "AyuMithra",
        welcome_subtitle: "देखभाल जो आपकी भाषा बोलती है",
        
        // Symptom Section
        select_symptoms: "अपने लक्षण चुनें",
        select_symptoms_desc: "सटीक विश्लेषण के लिए अपने अनुभव हो रहे सभी लक्षणों को चेक करें",
        analyze_symptoms: "लक्षणों का विश्लेषण करें",
        clear_all: "सभी साफ करें",
        ai_chatbot: "AI चैटबोट",
        
        // Results
        analysis_results: "विश्लेषण परिणाम",
        predicted_condition: "अनुमानित स्थिति",
        confidence: "विश्वास",
        description: "विवरण",
        precautions: "सावधानियां",
        severity: "गंभीरता",
        recommended_action: "अनुशंसित कार्रवाई",
        alternative_possibilities: "वैकल्पिक संभावनाएं",
        medical_disclaimer: "चिकित्सा अस्वीकरण",
        disclaimer_text: "यह उपकरण केवल सामान्य जानकारी प्रदान करता है और पेशेवर चिकित्सा सलाह का विकल्प नहीं है। उचित निदान और उपचार के लिए हमेशा स्वास्थ्य देखभा प्रदाता से परामर्श करें।",
        
        // Severity levels
        mild: "हल्का",
        moderate: "मध्यम",
        high: "गंभीर",
        
        // Actions
        consult_doctor: "डॉक्टर से परामर्श करें",
        rest_home: "घर पर आराम करें",
        monitor: "लक्षणों की निगरानी करें",
        seek_attention: "चिकित्सा ध्यान खोजें",
        
        // Chatbot
        chat_title: "AyuMithra सहायक",
        chat_placeholder: "अपना स्वास्थ्य प्रश्न लिखें...",
        chat_listening: "सुन रहा हूँ...",
        chat_transcribing: "प्रतिलेखन...",
        chat_welcome: "नमस्ते! मैं आपका AyuMithra स्वास्थ्य सहायक हूँ। मैं स्वास्थ्य संबंधी प्रश्नों, लक्षणों को समझने और रोग जानकारी प्रदान करने में आपकी मदद कर सकता हूँ। आप मुझसे अंग्रेजी, हिंदी या तेलुगु में टाइप या बोल सकते हैं!",
        
        // Info Cards
        how_it_works: "यह कैसे काम करता है",
        how_it_works_desc: "ऊपर दी गई सूची से अपने लक्षण चुनें और भविष्यवाणी प्राप्त करने के लिए 'लक्षणों का विश्लेषण करें' पर क्लिक करें।",
        accuracy: "सटीकता",
        accuracy_desc: "हमारा ML मॉडल सामान्य स्थितियों के लिए 97%+ सटीकता के साथ हजारों मामलों पर प्रशिक्षित है।",
        privacy: "गोपनीयता पहले",
        privacy_desc: "आपका स्वास्थ्य डेटा आपके डिवाइस पर रहता है। हम कोई व्यक्तिगत जानकारी संग्रहीत नहीं करते हैं।",
        
        // Buttons
        learn_more: "और जानें",
        get_started: "शुरू करें",
        back: "वापस",
        
        // Disease Detail
        disease_info: "बीमारी की जानकारी",
        associated_symptoms: "संबंधित लक्षण",
        related_diseases: "संबंधित बीमारियां",
        check_symptoms: "इस बीमारी के लक्षण जांचें"
    },
    
    te: {
        // Navigation
        symptom_checker: "లక్షణాల పరిశీలన",
        diseases: "వ్యాధులు",
        search_diseases: "వ్యాధులను వెతకండి...",
        
        // Header
        welcome_title: "AyuMithra",
        welcome_subtitle: "మీ భాష మాట్లాడే సంరక్షణ",
        
        // Symptom Section
        select_symptoms: "మీ లక్షణాలను ఎంచుకోండి",
        select_symptoms_desc: "ఖచ్చితమైన విశ్లేషణ కోసం మీరు అనుభవిస్తున్న అన్ని లక్షణాలను చెక్ చేయండి",
        analyze_symptoms: "లక్షణాలను విశ్లేషించండి",
        clear_all: "అన్నీ క్లియర్ చేయండి",
        ai_chatbot: "AI చాట్‌బాట్",
        
        // Results
        analysis_results: "విశ్లేషణ ఫలితాలు",
        predicted_condition: "అంచనా వేసిన పరిస్థితి",
        confidence: "విశ్వాసం",
        description: "వివరణ",
        precautions: "జాగ్రత్తలు",
        severity: "తీవ్రత",
        recommended_action: "సిఫార్సు చేయబడిన చర్య",
        alternative_possibilities: "ఇతర సాధ్యమైన వాటి",
        medical_disclaimer: "వైద్య DISCLAIMER",
        disclaimer_text: "ఈ సాధనం సాధారణ సమాచారాన్ని మాత్రమే అందిస్తుంది మరియు ప్రొఫెషనల్ వైద్య సలహాకు ప్రత్యామ్నాయం కాదు. సరైన రోగనిర్ధారణ మరియు చికిత్స కోసం ఎల్లప్పుడూ ఆరోగ్య సంరక్షణ ప్రదాతను సంప్రదించండి.",
        
        // Severity levels
        mild: "తేలిక",
        moderate: "మధ్యస్థం",
        high: "అధికం",
        
        // Actions
        consult_doctor: "డాక్టర్‌ను సంప్రదించండి",
        rest_home: "ఇంట్లో విశ్రాంతి తీసుకోండి",
        monitor: "లక్షణాలను పర్యవేక్షించండి",
        seek_attention: "వైద్య సహాయం పొందండి",
        
        // Chatbot
        chat_title: "AyuMithra సహాయకుడు",
        chat_placeholder: "మీ ఆరోగ్య ప్రశ్నను టైప్ చేయండి...",
        chat_listening: "వింటున్నాను...",
        chat_transcribing: "ట్రాన్స్‌క్రైబ్ చేస్తోంది...",
        chat_welcome: "నమస్తే! నేను మీ AyuMithra ఆరోగ్య సహాయకుడిని. నేను ఆరోగ్య సంబంధిత ప్రశ్నలు, లక్షణాలను అర్థం చేసుకోవడం మరియు వ్యాధి సమాచారం అందించడంలో మీకు సహాయం చేయగలను. మీరు నాతో ఆంగ్లం, హిందీ లేదా తెలుగులో టైప్ చేయవచ్చు లేదా మాట్లాడవచ్చు!",
        
        // Info Cards
        how_it_works: "ఇది ఎలా పనిచేస్తుంది",
        how_it_works_desc: "పైన ఉన్న జాబితా నుండి మీ లక్షణాలను ఎంచుకుని, భవిష్యవాణి పొందడానికి 'లక్షణాలను విశ్లేషించండి' పై క్లిక్ చేయండి.",
        accuracy: "ఖచ్చితత్వం",
        accuracy_desc: "మా ML మోడల్ సాధారణ పరిస్థితుల కోసం 97%+ ఖచ్చితత్వంతో వేలాది కేసులపై శిక్షణ పొందింది.",
        privacy: "గోప్యత మొదట",
        privacy_desc: "మీ ఆరోగ్య డేటా మీ డివైస్‌లోనే ఉంటుంది. మేము ఎటువంటి వ్యక్తిగత సమాచారాన్ని నిల్వ చేయము.",
        
        // Buttons
        learn_more: "మరింత తెలుసుకోండి",
        get_started: "ప్రారంభించండి",
        back: "వెనుకకు",
        
        // Disease Detail
        disease_info: "వ్యాధి సమాచారం",
        associated_symptoms: "సంబంధిత లక్షణాలు",
        related_diseases: "సంబంధిత వ్యాధులు",
        check_symptoms: "ఈ వ్యాధి యొక్క లక్షణాలను తనిఖీ చేయండి"
    }
};

// Disease translations
const diseaseTranslations = {
    en: {
        'Common Cold': 'Common Cold',
        'Flu': 'Flu',
        'Migraine': 'Migraine',
        'Food Poisoning': 'Food Poisoning',
        'COVID-19': 'COVID-19',
        'Dengue': 'Dengue',
        'Malaria': 'Malaria'
    },
    hi: {
        'Common Cold': 'सामान्य सर्दी',
        'Flu': 'फ्लू',
        'Migraine': 'माइग्रेन',
        'Food Poisoning': 'खाद्य विषाक्तता',
        'COVID-19': 'COVID-19',
        'Dengue': 'डेंगू',
        'Malaria': 'मलेरिया'
    },
    te: {
        'Common Cold': 'సాధారణ జలుబు',
        'Flu': 'ఫ్లూ',
        'Migraine': 'మైగ్రేన్',
        'Food Poisoning': 'ఆహార విషతుల్యత',
        'COVID-19': 'COVID-19',
        'Dengue': 'డెంగ్యూ',
        'Malaria': 'మలేరియా'
    }
};

// Disease descriptions
const diseaseDescriptions = {
    en: {
        'Common Cold': 'A viral infection of the upper respiratory tract. Usually harmless and resolves within a week.',
        'Flu': 'Influenza is a viral infection that attacks your respiratory system. More severe than common cold.',
        'Migraine': 'A headache of varying intensity, often accompanied by nausea and sensitivity to light and sound.',
        'Food Poisoning': 'Illness caused by consuming contaminated food or water. Symptoms include nausea, vomiting, and diarrhea.',
        'COVID-19': 'A respiratory illness caused by the SARS-CoV-2 virus. Can range from mild to severe.',
        'Dengue': 'A mosquito-borne viral infection causing high fever, severe headache, and joint pain.',
        'Malaria': 'A serious mosquito-borne disease causing fever, chills, and flu-like symptoms.'
    },
    hi: {
        'Common Cold': 'ऊपरी श्वसन पथ का वायरल संक्रमण। आमतौर पर हानिकारक नहीं और एक सप्ताह में ठीक हो जाता है।',
        'Flu': 'इन्फ्लुएंजा एक वायरल संक्रमण है जो आपकी श्वसन प्रणाली को प्रभावित करता है। सामान्य सर्दी से अधिक गंभीर।',
        'Migraine': 'तीव्रता में भिन्नता वाला सिरदर्द, अक्सर मतली और रोशनी और आवाज के प्रति संवेदनशीलता के साथ।',
        'Food Poisoning': 'दूषित भोजन या पानी के सेवन से होने वाली बीमारी। लक्षणों में मतली, उल्टी और दस्त शामिल हैं।',
        'COVID-19': 'SARS-CoV-2 वायरस से होने वाली श्वसन बीमारी। हल्के से गंभीर तक हो सकता है।',
        'Dengue': 'मच्छर से फैलने वाला वायरल संक्रमण जिससे उच्च बुखार, तेज सिरदर्द और जोड़ों का दर्द होता है।',
        'Malaria': 'गंभीर मच्छर जनित बीमारी जिससे बुखार, ठंड लगना और फ्लू जैसे लक्षण होते हैं।'
    },
    te: {
        'Common Cold': 'ఎగువ శ్వాస మార్గంలో వైరల్ సోకు. సాధారణంగా హానికరం కాదు మరియు ఒక వారంలోనే తగ్గుతుంది.',
        'Flu': 'ఇన్ఫ్లుయెంజా అనేది మీ శ్వాస వ్యవస్థను దాడి చేసే వైరల్ సోకు. సాధారణ జలుబు కంటే తీవ్రమైనది.',
        'Migraine': 'తీవ్రతలో మార్పులు ఉండే తలనొప్పి, తరచుగా వాంతులు మరియు కాంతి మరియు శబ్దానికి బాధతో కూడుకున్నది.',
        'Food Poisoning': 'కలుషితమైన ఆహారం లేదా నీరు తీసుకోవడం వల్ల వచ్చే అనారోగ్యం. లక్షణాలలో వాంతులు, వాంతులు మరియు అతిసారం ఉంటాయి.',
        'COVID-19': 'SARS-CoV-2 వైరస్ వల్ల కలిగే శ్వాస రోగం. తేలిక నుండి తీవ్రంగా ఉండవచ్చు.',
        'Dengue': 'దోమల ద్వారా వ్యాపించే వైరల్ సోకు, ఇది ఎక్కువ జ్వరం, తీవ్రమైన తలనొప్పి మరియు కీళ్ల నొప్పులను కలిగిస్తుంది.',
        'Malaria': 'తీవ్రమైన దోమ సంబంధిత వ్యాధి, ఇది జ్వరం, జలుబు మరియు ఫ్లూ లాంటి లక్షణాలను కలిగిస్తుంది.'
    }
};

// Symptom translations
const symptomTranslations = {
    en: {
        'Fever': 'Fever',
        'Cough': 'Cough',
        'Sore Throat': 'Sore Throat',
        'Runny Nose': 'Runny Nose',
        'Sneezing': 'Sneezing',
        'Body Aches': 'Body Aches',
        'Fatigue': 'Fatigue',
        'Headache': 'Headache',
        'Chills': 'Chills',
        'Nausea': 'Nausea',
        'Vomiting': 'Vomiting',
        'Diarrhea': 'Diarrhea',
        'Abdominal Pain': 'Abdominal Pain',
        'Loss of Taste': 'Loss of Taste',
        'Loss of Smell': 'Loss of Smell',
        'Shortness of Breath': 'Shortness of Breath',
        'Chest Pain': 'Chest Pain',
        'Sensitivity to Light': 'Sensitivity to Light',
        'Sensitivity to Sound': 'Sensitivity to Sound',
        'Dizziness': 'Dizziness',
        'Rash': 'Rash',
        'Joint Pain': 'Joint Pain',
        'Muscle Pain': 'Muscle Pain',
        'Sweating': 'Sweating',
        'Loss of Appetite': 'Loss of Appetite'
    },
    hi: {
        'Fever': 'बुखार',
        'Cough': 'खांसी',
        'Sore Throat': 'गले में खराश',
        'Runny Nose': 'बहती नाक',
        'Sneezing': 'छींक',
        'Body Aches': 'शरीर में दर्द',
        'Fatigue': 'थकान',
        'Headache': 'सिरदर्द',
        'Chills': 'ठंड लगना',
        'Nausea': 'मतली',
        'Vomiting': 'उल्टी',
        'Diarrhea': 'दस्त',
        'Abdominal Pain': 'पेट दर्द',
        'Loss of Taste': 'स्वाद का न आना',
        'Loss of Smell': 'गंध का न आना',
        'Shortness of Breath': 'सांस फूलना',
        'Chest Pain': 'छाती में दर्द',
        'Sensitivity to Light': 'रोशनी से परेशानी',
        'Sensitivity to Sound': 'आवाज से परेशानी',
        'Dizziness': 'चक्कर आना',
        'Rash': 'चकत्ते',
        'Joint Pain': 'जोड़ों का दर्द',
        'Muscle Pain': 'मांसपेशी दर्द',
        'Sweating': 'पसीना',
        'Loss of Appetite': 'भूख न लगना'
    },
    te: {
        'Fever': 'జ్వరం',
        'Cough': 'దగ్గు',
        'Sore Throat': 'గొంతు నొప్పి',
        'Runny Nose': 'జలుబు',
        'Sneezing': 'దుమ్ము',
        'Body Aches': 'శరీర నొప్పులు',
        'Fatigue': 'అలసట',
        'Headache': 'తలనొప్పి',
        'Chills': 'జలుబు',
        'Nausea': 'వాంతి వచ్చే అనుభూతి',
        'Vomiting': 'వాంతులు',
        'Diarrhea': 'అతిసారం',
        'Abdominal Pain': 'కడుపు నొప్పి',
        'Loss of Taste': 'రుచి తెలియకపోవడం',
        'Loss of Smell': 'వాసన తెలియకపోవడం',
        'Shortness of Breath': 'శ్వాస ఆడకపోవడం',
        'Chest Pain': 'ఛాతీ నొప్పి',
        'Sensitivity to Light': 'కాంతికి బాధ',
        'Sensitivity to Sound': 'శబ్దానికి బాధ',
        'Dizziness': 'తలతిరుగుడు',
        'Rash': 'దద్దులు',
        'Joint Pain': 'కీళ్ల నొప్పి',
        'Muscle Pain': 'కండరాల నొప్పి',
        'Sweating': 'చెమట',
        'Loss of Appetite': 'ఆకలి లేకపోవడం'
    }
};

// Language Switcher Class
class LanguageSwitcher {
    constructor() {
        this.currentLang = localStorage.getItem('ayumithra-language') || 'en';
        this.langBtn = document.getElementById('langBtn');
        this.langDropdown = document.getElementById('langDropdown');
        this.currentLangSpan = document.getElementById('currentLang');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setLanguage(this.currentLang, false);
    }
    
    setupEventListeners() {
        // Toggle dropdown
        this.langBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            this.closeDropdown();
        });
        
        // Language options
        const langOptions = this.langDropdown.querySelectorAll('.lang-option');
        langOptions.forEach(option => {
            option.addEventListener('click', (e) => {
                e.stopPropagation();
                const lang = option.dataset.lang;
                this.setLanguage(lang);
                this.closeDropdown();
            });
        });
    }
    
    toggleDropdown() {
        const parent = this.langBtn.closest('.language-switcher');
        parent.classList.toggle('active');
    }
    
    closeDropdown() {
        const parent = this.langBtn.closest('.language-switcher');
        parent.classList.remove('active');
    }
    
    setLanguage(lang, save = true) {
        if (!translations[lang]) return;
        
        this.currentLang = lang;
        
        // Update UI
        this.currentLangSpan.textContent = lang.toUpperCase();
        
        // Update active state in dropdown
        const langOptions = this.langDropdown.querySelectorAll('.lang-option');
        langOptions.forEach(option => {
            option.classList.toggle('active', option.dataset.lang === lang);
        });
        
        // Update all translatable elements
        this.updatePageTranslations();
        
        // Save preference
        if (save) {
            localStorage.setItem('ayumithra-language', lang);
        }
        
        // Update HTML lang attribute
        document.documentElement.lang = lang === 'en' ? 'en' : (lang === 'hi' ? 'hi' : 'te');
        
        // Dispatch event for other components
        window.dispatchEvent(new CustomEvent('languageChanged', { detail: { language: lang } }));
    }
    
    updatePageTranslations() {
        const t = translations[this.currentLang];
        
        // Update elements with data-translate attribute
        document.querySelectorAll('[data-translate]').forEach(el => {
            const key = el.dataset.translate;
            if (t[key]) {
                el.textContent = t[key];
            }
        });
        
        // Update placeholders
        document.querySelectorAll('[data-translate-placeholder]').forEach(el => {
            const key = el.dataset.translatePlaceholder;
            if (t[key]) {
                el.placeholder = t[key];
            }
        });
        
        // Update symptom names
        this.translateSymptoms();
        
        // Update disease names and descriptions
        this.translateDiseases();
    }
    
    translateSymptoms() {
        const st = symptomTranslations[this.currentLang];
        if (!st) return;
        
        // Update symptom labels in the grid
        document.querySelectorAll('.symptom-name').forEach(el => {
            const englishName = el.dataset.englishName || el.textContent;
            if (!el.dataset.englishName) {
                el.dataset.englishName = englishName; // Store original
            }
            if (st[englishName]) {
                el.textContent = st[englishName];
            }
        });
    }
    
    getTranslation(key) {
        const t = translations[this.currentLang];
        return t[key] || key;
    }
    
    getSymptomTranslation(englishSymptom) {
        const st = symptomTranslations[this.currentLang];
        return st[englishSymptom] || englishSymptom;
    }
    
    getDiseaseTranslation(englishDisease) {
        const dt = diseaseTranslations[this.currentLang];
        if (!dt) {
            console.warn('No disease translations found for language:', this.currentLang);
            return englishDisease;
        }
        return dt[englishDisease] || englishDisease;
    }
    
    getDiseaseDescription(englishDisease) {
        const dd = diseaseDescriptions[this.currentLang];
        if (!dd) {
            console.warn('No disease descriptions found for language:', this.currentLang);
            return englishDisease;
        }
        return dd[englishDisease] || englishDisease;
    }
    
    getCurrentLanguage() {
        return this.currentLang;
    }
    
    // Translate disease names on the page
    translateDiseases() {
        const dt = diseaseTranslations[this.currentLang];
        if (!dt) return;
        
        // Update disease names in results
        document.querySelectorAll('.disease-name').forEach(el => {
            const englishName = el.dataset.englishName || el.textContent;
            if (!el.dataset.englishName) {
                el.dataset.englishName = englishName;
            }
            if (dt[englishName]) {
                el.textContent = dt[englishName];
            }
        });
        
        // Update disease descriptions
        document.querySelectorAll('.disease-description').forEach(el => {
            const englishDesc = el.dataset.englishDesc;
            if (englishDesc) {
                const dd = diseaseDescriptions[this.currentLang];
                if (dd && dd[englishDesc]) {
                    el.textContent = dd[englishDesc];
                }
            }
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.languageSwitcher = new LanguageSwitcher();
}); 