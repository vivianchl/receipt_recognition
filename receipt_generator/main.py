import sys
import os
import glob
import datetime

def get_background(backgrounds, index):
    # Get the background filename in a round-robin fashion
    return backgrounds[index % len(backgrounds)]

def call_scripts(number_of_calls):
    # Define the folders containing the script files and backgrounds
    script_folder = "scripts"
    background_folder = "backgrounds"

    # Get all Python script files from the script folder
    script_files = glob.glob(os.path.join(script_folder, "*.py"))

    # Get all background files from the background folder
    backgrounds = glob.glob(os.path.join(background_folder, "*"))

    # Calculate the number of scripts
    num_scripts = len(script_files)

    # Determine the number of scripts to call based on the number of calls
    scripts_to_call = min(number_of_calls, num_scripts)

    # Calculate the number of calls per script
    calls_per_script = max(number_of_calls // scripts_to_call, 1)

    # Initialize the index to track the current background
    background_index = 0

    # Iterate over each script file and call it the appropriate number of times
    for i in range(scripts_to_call):
        # Get the script file
        script_file = script_files[i]

        # Check if the script file exists
        if not os.path.exists(script_file):
            print(f"Error: Script file '{script_file}' not found.")
            return

        for x in range(calls_per_script):        
            # Get the background filename
            background = get_background(backgrounds, background_index)

            # Call the script with the background filename as an argument
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            image_name = f"IMG_{timestamp}.png"
            os.system(f"python {script_file}")
            os.system(f"python receipt_background_generator.py {background} {image_name}")
            # Increment the background index
            background_index += 1
            print(f"Image {background_index}/{number_of_calls} erfolgreich erstellt")

if __name__ == "__main__":
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python main_script.py <number_of_calls>")
        sys.exit(1)

    # Get the number of calls from the command-line arguments
    try:
        number_of_calls = int(sys.argv[1])
    except ValueError:
        print("Error: Please provide a valid number of calls.")
        sys.exit(1)

    # Call the function to execute the selected scripts
    call_scripts(number_of_calls)
