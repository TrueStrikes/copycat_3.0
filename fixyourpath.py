config_file_path = 'config.json'

# Open the config.json file for reading as plain text
with open(config_file_path, 'r') as file:
    config_text = file.read()

# Replace backslashes with forward slashes in the content
config_text = config_text.replace("\\", "/")

# Write the modified text back to the file
with open(config_file_path, 'w') as file:
    file.write(config_text)

print(f'Backslashes in {config_file_path} have been replaced with forward slashes.')

# Wait for user input to close the program
input("Press Enter to exit...")
