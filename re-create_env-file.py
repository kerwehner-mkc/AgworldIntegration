import os
import re

# Define file paths
env_file = ".env"
env_example_file = ".env.example"
script_file = "insertoperator_licenses.py" # Path to the script that contains the required_vars list

def extract_required_vars(script_path):
    """Extract required environment variables from the script."""
    required_vars = []
    with open(script_path, "r") as script:
        for line in script:
            match = re.search(r'required_vars\s*=\s*\[([^\]]+)\]', line)
            if match:
                # Extract variables from the list
                vars_list = match.group(1).replace('"', '').replace("'", "").split(",")
                required_vars.extend(var.strip() for var in vars_list)
    return set(required_vars)

def create_env_example(env_path, env_example_path, required_vars):
    """Create an .env.example file with comments for required variables."""
    with open(env_path, "r") as infile, open(env_example_path, "w") as outfile:
        for line in infile:
            if line.strip().startswith("#") or not line.strip():
                # Write comments and empty lines as-is
                outfile.write(line)
            else:
                # Split the line at the first '='
                key = line.split("=", 1)[0]
                if key in required_vars:
                    outfile.write(f"{key}=  # REQUIRED\n")
                else:
                    outfile.write(f"{key}=\n")
    print(f"Example .env file created: {env_example_path}")

def main():
    # Extract required variables from the script
    required_vars = extract_required_vars(script_file)
    print(f"Required variables found in {script_file}: {', '.join(required_vars)}")

    # Create the .env.example file
    create_env_example(env_file, env_example_file, required_vars)

if __name__ == "__main__":
    main()