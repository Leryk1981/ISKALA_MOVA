// MOVA - DOM manipulation and event handling
document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('submitBtn');
    const form = document.querySelector('form');
    
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const input = document.getElementById('userInput');
        const value = input.value;
        
        // JALM - business logic
        const processedValue = processUserInput(value);
        const result = calculateResult(processedValue);
        
        // CODE - general code
        if (result.isValid) {
            displayResult(result.data);
        } else {
            handleError(result.error);
        }
    });
});

// JALM - business logic functions
function processUserInput(input) {
    return input.trim().toLowerCase();
}

function calculateResult(data) {
    const result = {
        isValid: data.length > 0,
        data: data,
        error: null
    };
    
    if (!result.isValid) {
        result.error = 'Input is empty';
    }
    
    return result;
}

// CODE - utility functions
function displayResult(data) {
    const output = document.getElementById('output');
    output.innerHTML = `<p>Result: ${data}</p>`;
    
    // LOG - logging
    console.log('Result displayed:', data);
}

function handleError(error) {
    // ERROR - error handling
    console.error('Error occurred:', error);
    alert('Error: ' + error);
}

// CODE - additional functionality
const config = {
    apiUrl: 'https://api.example.com',
    timeout: 5000,
    retries: 3
};

// LOG - more logging
console.info('Application initialized');
console.warn('This is a test application'); 