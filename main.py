import subprocess
import sys
import os

def main():
    """Run the Gradescope scraper script"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    gradescope_script = os.path.join(script_dir, 'gradescope.py')
    
    if not os.path.exists(gradescope_script):
        print("Error: gradescope.py not found in the same directory")
        sys.exit(1)
    
    print("Running Gradescope scraper...")
    try:
        subprocess.run([sys.executable, gradescope_script], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running gradescope.py: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nScraper interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
