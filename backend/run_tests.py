import pytest
import sys

def main():
    """Test süitini çalıştırır."""
    args = [
        "--verbose",
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "-m", "not integration",  # integration testlerini hariç tut
        "tests"
    ]
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main() 