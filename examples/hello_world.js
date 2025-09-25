// Example: Hello World in JavaScript
// This shows how to add JavaScript code to the sz project

/**
 * Returns a greeting message
 * @param {string} name - The name to greet (defaults to "World")
 * @returns {string} A greeting message
 */
function helloWorld(name = "World") {
    return `Hello, ${name}!`;
}

// Example usage
if (typeof module !== 'undefined' && module.exports) {
    // Node.js environment
    module.exports = helloWorld;
} else {
    // Browser environment
    console.log(helloWorld());
    console.log(helloWorld("sz Project"));
}