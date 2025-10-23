from flask import Flask, request, jsonify, render_template
import os
import subprocess # WARNING: Using subprocess directly with user input is a huge security risk!
                   # This is for conceptual understanding only.
                   # A real implementation requires heavy sandboxing and validation.

app = Flask(__name__)

# A very basic, in-memory simulated file system for demonstration
# In a real app, this would be per-user and persistent (database/actual files)
file_system = {
    '~': {
        'my_script.py': 'print("Hello from WebPi!")\nimport os\nprint(os.getcwd())',
        'README.md': '# Welcome to WebPi!\n\nThis is your simulated Raspberry Pi environment.'
    },
    '~bin': { # Just for example, not a real bin
        'mycommand': 'echo "This is a custom command output"'
    }
}
current_user_path = '~' # Simulate user's current working directory

def get_current_dir_content():
    global current_user_path
    path_segments = current_user_path.split('/')
    current_dir = file_system
    for segment in path_segments:
        if segment == '~':
            current_dir = file_system['~']
        elif segment in current_dir and isinstance(current_dir[segment], dict):
            current_dir = current_dir[segment]
        else:
            return None # Path not found
    return current_dir

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/execute_command', methods=['POST'])
def execute_command():
    global current_user_path
    data = request.json
    command = data.get('command', '').strip()

    output = ""
    error = ""
    new_path = current_user_path

    parts = command.split(' ', 1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ''

    # --- SIMULATED COMMANDS (very basic) ---
    if cmd == 'ls':
        current_dir_content = get_current_dir_content()
        if current_dir_content is not None:
            output = "\n".join(sorted(current_dir_content.keys()))
        else:
            error = f"ls: cannot access '{current_user_path}': No such file or directory"
    elif cmd == 'cd':
        target_path = args
        if not target_path:
            new_path = '~' # Go to home if no argument
        else:
            resolved_path = os.path.normpath(os.path.join(current_user_path, target_path))
            # Very simplistic path validation:
            if resolved_path == '~': # Handle explicit home
                new_path = '~'
            elif resolved_path.startswith('~'): # Ensure paths stay within user's 'home'
                # Check if the target directory exists in our simulated FS
                path_segments = resolved_path.split('/')
                temp_dir = file_system
                path_found = True
                for segment in path_segments[1:]: # Skip '~'
                    if segment in temp_dir and isinstance(temp_dir[segment], dict):
                        temp_dir = temp_dir[segment]
                    else:
                        path_found = False
                        break
                if path_found:
                    new_path = resolved_path
                else:
                    error = f"cd: no such file or directory: {target_path}"
            else:
                error = f"cd: permission denied: {target_path}" # For security, assume outside home is denied

    elif cmd == 'cat':
        filename = args
        current_dir_content = get_current_dir_content()
        if current_dir_content and filename in current_dir_content and isinstance(current_dir_content[filename], str):
            output = current_dir_content[filename]
        else:
            error = f"cat: {filename}: No such file or directory"
    elif cmd == 'python' or cmd == 'python3':
        script_name = args.strip()
        if not script_name:
            output = "Python interactive shell is not simulated here. Please run a script."
        else:
            current_dir_content = get_current_dir_content()
            if current_dir_content and script_name in current_dir_content and isinstance(current_dir_content[script_name], str):
                # Execute Python in a very limited, sandboxed way (EVAL/EXEC are DANGEROUS!)
                # For a real system, you'd execute this in a separate, isolated process/container.
                try:
                    # Capture stdout and stderr
                    import io
                    import sys
                    old_stdout = sys.stdout
                    old_stderr = sys.stderr
                    redirected_output = io.StringIO()
                    redirected_error = io.StringIO()
                    sys.stdout = redirected_output
                    sys.stderr = redirected_error

                    exec(current_dir_content[script_name], {'os': None, 'subprocess': None, '__builtins__': {}}) # Very limited builtins
                    output = redirected_output.getvalue()
                    error = redirected_error.getvalue()
                except Exception as e:
                    error = f"Error executing Python script: {e}"
                finally:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
            else:
                error = f"python: can't open file '{script_name}': No such file or directory"
    elif cmd == 'echo':
        output = args
    elif cmd == 'clear':
        output = "" # Frontend will clear the screen
    elif cmd == 'nano':
        filename = args
        output = f"Simulating nano editor for '{filename}'. (No actual editor here yet)"
        # In a real system, this would open a text editor component
    elif cmd == 'whoami':
        output = "pi"
    elif cmd == 'pwd':
        output = current_user_path
    elif cmd == 'date':
        import datetime
        output = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
    else:
        error = f"{cmd}: command not found"

    # In a production system, you'd run actual commands in a sandboxed environment
    # using subprocess in a highly controlled manner, or better yet, a dedicated
    # virtual machine or container for each user.

    return jsonify({'output': output, 'error': error, 'new_path': new_path})

if __name__ == '__main__':
    # To run this:
    # 1. Save all files in the same directory.
    # 2. Make sure you have Flask installed (`pip install Flask`).
    # 3. From your terminal, navigate to the directory and run: `python app.py`
    # 4. Open your browser to `http://127.0.0.1:5000/`
    app.run(debug=True)
