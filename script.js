document.addEventListener('DOMContentLoaded', () => {
    const terminal = document.getElementById('terminal');
    const commandInput = document.getElementById('commandInput');
    const currentInputSpan = document.getElementById('current-input');

    let commandHistory = [];
    let historyIndex = -1;

    // Simulate current directory (client-side for display purposes)
    let currentPath = '~';

    function addLineToTerminal(text, className = 'output') {
        const div = document.createElement('div');
        div.classList.add('line', className);
        div.textContent = text;
        terminal.appendChild(div);
        terminal.scrollTop = terminal.scrollHeight; // Auto-scroll to bottom
    }

    function addPrompt(path = currentPath) {
        const promptDiv = document.createElement('div');
        promptDiv.classList.add('line', 'prompt');
        promptDiv.innerHTML = `<span>pi@webpi</span>:${path}$ <span id="current-input"></span>`;
        terminal.appendChild(promptDiv);
        terminal.scrollTop = terminal.scrollHeight;
        // Re-assign currentInputSpan to the new one for live typing
        document.getElementById('current-input').id = ''; // Remove old ID
        currentInputSpan = promptDiv.querySelector('span:last-child'); // Update the reference
    }

    function processCommand(command) {
        if (!command.trim()) {
            addPrompt();
            return;
        }

        commandHistory.unshift(command); // Add to history
        historyIndex = -1; // Reset history index

        // Display the typed command
        addLineToTerminal(`pi@webpi:${currentPath}$ ${command}`, 'command');

        // --- Send command to backend (simplified fetch) ---
        fetch('/execute_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: command }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.output) {
                addLineToTerminal(data.output, 'output');
            }
            if (data.error) {
                addLineToTerminal(data.error, 'error');
            }
            if (data.new_path) {
                currentPath = data.new_path; // Update client-side path
            }
            addPrompt(currentPath); // Add new prompt after command execution
        })
        .catch(error => {
            console.error('Error:', error);
            addLineToTerminal(`Error connecting to backend: ${error.message}`, 'error');
            addPrompt();
        });
    }

    commandInput.addEventListener('keydown', (e) => {
        // Update the span to show what's being typed
        currentInputSpan.textContent = commandInput.value;

        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent new line in input field
            const command = commandInput.value;
            commandInput.value = ''; // Clear input field
            currentInputSpan.textContent = ''; // Clear span

            processCommand(command);

        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (commandHistory.length > 0 && historyIndex < commandHistory.length - 1) {
                historyIndex++;
                commandInput.value = commandHistory[historyIndex];
                currentInputSpan.textContent = commandInput.value; // Update span
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (historyIndex > 0) {
                historyIndex--;
                commandInput.value = commandHistory[historyIndex];
                currentInputSpan.textContent = commandInput.value; // Update span
            } else if (historyIndex === 0) {
                historyIndex = -1;
                commandInput.value = '';
                currentInputSpan.textContent = ''; // Clear span
            }
        }
    });

    // Handle typing in the input field to update the current-input span
    commandInput.addEventListener('input', () => {
        currentInputSpan.textContent = commandInput.value;
    });

    // Initial prompt
    addPrompt();
    commandInput.focus();
});
