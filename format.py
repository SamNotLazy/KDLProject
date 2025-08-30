import json

# Define the input and output filenames
input_filename = 'plotlycustommaplayoutmd.json'
output_filename = 'output.json'

# --- Instructions ---
# 1. Create a file named 'input.json' in the same directory as this script.
# 2. Copy your JSON data into 'input.json'.
# 3. Run this script.
# 4. The modified JSON will be saved in 'output.json'.

try:
    # Open the input file and load the JSON data
    with open(input_filename, 'r') as f:
        json_data = json.load(f)

    # Iterate through each state/territory in the JSON data
    for state, state_data in json_data.items():
        # Check if 'districts' key exists
        if 'districts' in state_data:
            # Get the original districts dictionary
            original_districts = state_data['districts']

            # Create a new dictionary with capitalized keys
            # This is done to avoid changing the dictionary while iterating over it
            capitalized_districts = {key.upper(): value for key, value in original_districts.items()}

            # Replace the old districts dictionary with the new one
            state_data['districts'] = capitalized_districts

    # Open the output file and write the modified JSON data
    with open(output_filename, 'w') as f:
        json.dump(json_data, f, indent=4)

    print(f"Successfully processed '{input_filename}' and saved the output to '{output_filename}'.")

except FileNotFoundError:
    print(f"Error: The file '{input_filename}' was not found.")
    print("Please create it and paste your JSON data inside.")
except json.JSONDecodeError:
    print(f"Error: The data in '{input_filename}' is not valid JSON. Please check the file's content.")

