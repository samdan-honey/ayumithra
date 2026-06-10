// Health ML App - Frontend JavaScript

// Icon injection helper function
function injectIcons() {
    const iconMap = {
        'icon-hospital': Icons.hospital,
        'icon-search': Icons.search,
        'icon-refresh': Icons.refresh,
        'icon-description': Icons.description,
        'icon-warning': Icons.warning,
        'icon-shield': Icons.shield,
        'icon-lightbulb': Icons.lightbulb,
        'icon-alert': Icons.alertOctagon,
        'icon-severity-mild': Icons.severityMild,
        'icon-severity-moderate': Icons.severityModerate,
        'icon-severity-high': Icons.severityHigh,
        'icon-list': Icons.list
    };

    Object.keys(iconMap).forEach(className => {
        const elements = document.querySelectorAll('.' + className);
        elements.forEach(el => {
            el.innerHTML = iconMap[className];
        });
    });
}

// Disease Dropdown functionality
let allDiseases = [];

async function loadDiseases() {
    try {
        const response = await fetch('/diseases');
        const data = await response.json();
        if (data.success) {
            allDiseases = data.diseases;
            populateDiseaseDropdown(allDiseases);
        }
    } catch (error) {
        console.error('Error loading diseases:', error);
    }
}

function populateDiseaseDropdown(diseases) {
    const dropdownItems = document.getElementById('diseaseDropdownItems');
    
    if (diseases.length === 0) {
        dropdownItems.innerHTML = '<div class="dropdown-empty">No diseases found</div>';
        return;
    }
    
    dropdownItems.innerHTML = diseases.map(disease => {
        const severityClass = `severity-${disease.severity_level.toLowerCase()}-indicator`;
        return `
            <a href="/disease/${disease.id}" class="dropdown-item">
                <span class="severity-indicator ${severityClass}"></span>
                ${disease.name}
            </a>
        `;
    }).join('');
}

function filterDiseases(searchTerm) {
    const filtered = allDiseases.filter(disease => 
        disease.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    populateDiseaseDropdown(filtered);
}

function initDropdown() {
    const dropdownBtn = document.getElementById('diseaseDropdownBtn');
    const dropdown = document.querySelector('.dropdown');
    const searchInput = document.getElementById('diseaseSearch');
    
    // Toggle dropdown
    dropdownBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('active');
        if (dropdown.classList.contains('active')) {
            searchInput.focus();
        }
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        if (!dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
    
    // Search functionality
    searchInput.addEventListener('input', (e) => {
        filterDiseases(e.target.value);
    });
    
    // Prevent dropdown from closing when clicking inside
    document.querySelector('.dropdown-menu').addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    // Inject SVG icons
    injectIcons();
    
    // Initialize dropdown
    initDropdown();
    
    // Load diseases for dropdown
    loadDiseases();
    // DOM Elements
    const predictBtn = document.getElementById('predictBtn');
    const clearBtn = document.getElementById('clearBtn');
    const symptomsGrid = document.getElementById('symptomsGrid');
    const resultSection = document.getElementById('resultSection');
    const loadingSection = document.getElementById('loadingSection');
    
    // Result elements
    const predictedDisease = document.getElementById('predictedDisease');
    const confidenceText = document.getElementById('confidenceText');
    const confidenceBadge = document.getElementById('confidenceBadge');
    const diseaseDescription = document.getElementById('diseaseDescription');
    const severityLevel = document.getElementById('severityLevel');
    const precautions = document.getElementById('precautions');
    const recommendedAction = document.getElementById('recommendedAction');
    const alternativeList = document.getElementById('alternativeList');

    // Event Listeners
    predictBtn.addEventListener('click', handlePredict);
    clearBtn.addEventListener('click', handleClear);

    // Get selected symptoms
    function getSelectedSymptoms() {
        const checkboxes = symptomsGrid.querySelectorAll('input[type="checkbox"]:checked');
        return Array.from(checkboxes).map(cb => cb.value);
    }

    // Handle predict button click
    async function handlePredict() {
        const selectedSymptoms = getSelectedSymptoms();
        
        if (selectedSymptoms.length === 0) {
            alert('Please select at least one symptom before analyzing.');
            return;
        }

        // Show loading, hide results
        resultSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ symptoms: selectedSymptoms })
            });
            
            // Check if response is OK
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `Server error: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Prediction response:', data); // Debug log
            
            if (data.success) {
                displayResults(data);
            } else {
                throw new Error(data.error || 'Failed to get prediction');
            }
        } catch (error) {
            console.error('Prediction Error:', error);
            
            // Show user-friendly error message with actual error
            let errorMessage = 'An error occurred while analyzing symptoms. ';
            
            if (error.message.includes('Model not loaded')) {
                errorMessage += 'The model is not loaded. Please restart the application.';
            } else if (error.message.includes('NetworkError') || error.message.includes('fetch')) {
                errorMessage += 'Network error. Please check your connection and try again.';
            } else if (error.message.includes('Invalid symptoms')) {
                errorMessage += 'Please refresh the page and select symptoms again.';
            } else {
                errorMessage += `Error details: ${error.message}. Please try again. If the problem persists, refresh the page.`;
            }
            
            alert(errorMessage);
        } finally {
            loadingSection.classList.add('hidden');
        }
    }

    // Display prediction results
    function displayResults(data) {
        const prediction = data.prediction;
        const allPredictions = data.all_predictions;
        
        if (!prediction) {
            console.error('No prediction data received:', data);
            alert('No prediction results. Please try again.');
            return;
        }
        
        // Main prediction - store English name for translation
        const englishDiseaseName = prediction.disease;
        predictedDisease.dataset.englishName = englishDiseaseName;
        
        // Translate disease name if language switcher is available
        if (window.languageSwitcher) {
            try {
                predictedDisease.textContent = window.languageSwitcher.getDiseaseTranslation(englishDiseaseName);
            } catch (e) {
                console.error('Error translating disease name:', e);
                predictedDisease.textContent = englishDiseaseName;
            }
        } else {
            predictedDisease.textContent = englishDiseaseName;
        }
        
        confidenceText.textContent = `Confidence: ${prediction.confidence.toFixed(1)}%`;
        
        // Confidence badge
        confidenceBadge.className = 'confidence-badge';
        if (prediction.confidence >= 70) {
            confidenceBadge.classList.add('confidence-high');
            confidenceBadge.textContent = 'High Confidence';
        } else if (prediction.confidence >= 40) {
            confidenceBadge.classList.add('confidence-medium');
            confidenceBadge.textContent = 'Medium Confidence';
        } else {
            confidenceBadge.classList.add('confidence-low');
            confidenceBadge.textContent = 'Low Confidence';
        }
        
        // Disease details - store English description for translation
        const englishDescription = prediction.description;
        diseaseDescription.dataset.englishDesc = englishDiseaseName; // Use disease name as key
        
        if (window.languageSwitcher) {
            try {
                diseaseDescription.textContent = window.languageSwitcher.getDiseaseDescription(englishDiseaseName);
            } catch (e) {
                console.error('Error translating disease description:', e);
                diseaseDescription.textContent = englishDescription || 'No description available.';
            }
        } else {
            diseaseDescription.textContent = englishDescription || 'No description available.';
        }
        
        precautions.textContent = prediction.precautions || 'No precautions available.';
        recommendedAction.textContent = prediction.recommended_action || 'No recommended action available.';
        
        // Severity level
        severityLevel.className = 'severity-badge';
        if (prediction.severity_level === 'Mild') {
            severityLevel.classList.add('severity-mild');
        } else if (prediction.severity_level === 'Moderate') {
            severityLevel.classList.add('severity-moderate');
        } else {
            severityLevel.classList.add('severity-high');
        }
        severityLevel.textContent = prediction.severity_level || 'Unknown';
        
        // Alternative predictions (excluding the top one)
        alternativeList.innerHTML = '';
        if (allPredictions && allPredictions.length > 1) {
            allPredictions.slice(1).forEach(pred => {
                const item = document.createElement('div');
                item.className = 'alternative-item';
                item.innerHTML = `
                    <span class="alternative-name">${pred.disease}</span>
                    <span class="alternative-probability">${pred.probability.toFixed(1)}%</span>
                `;
                alternativeList.appendChild(item);
            });
        } else {
            alternativeList.innerHTML = '<p style="color: #666;">No other significant matches found.</p>';
        }
        
        // Show results
        resultSection.classList.remove('hidden');
        
        // Scroll to results
        resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    // Handle clear button click
    function handleClear() {
        const checkboxes = symptomsGrid.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = false;
        });
        
        resultSection.classList.add('hidden');
        loadingSection.classList.add('hidden');
    }

    // Add keyboard shortcut (Enter to predict, Escape to clear)
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            handlePredict();
        } else if (e.key === 'Escape') {
            handleClear();
        }
    });
});
