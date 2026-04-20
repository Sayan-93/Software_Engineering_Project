import subprocess
import sys

def run_command(command, description):
    print(f"\n {description}...")
    result = subprocess.run(command, shell=True)
    
    if result.returncode != 0:
        print(f" Failed: {description}")
        sys.exit(1)
    else:
        print(f" Done: {description}")

if __name__ == "__main__":
    print(" Starting backend setup...\n")


    # Seed database
    run_command("python seed.py", "Seeding database")

    # Run indexing
    run_command("python run_index.py", "Running AI indexing")

    # Pre-download models
    run_command("python pre_download.py", "Downloading models")

    # Start Flask app
    print("\n Starting Flask server...\n")
    subprocess.run("python app.py", shell=True)