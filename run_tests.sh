#!/bin/bash

# Test runner script for Viral Fashion Agent
# Usage: ./run_tests.sh [options]

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}Viral Fashion Agent - Test Runner${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest not found${NC}"
    echo "Install dependencies: pip install -r requirements.txt"
    exit 1
fi

# Default to all tests with coverage
if [ $# -eq 0 ]; then
    echo -e "${YELLOW}Running all tests with coverage...${NC}"
    pytest --cov=src --cov-report=term-missing --cov-report=html --cov-fail-under=85
    
    echo ""
    echo -e "${GREEN}✅ Tests completed!${NC}"
    echo -e "${YELLOW}📊 Coverage report: htmlcov/index.html${NC}"
    
else
    # Handle command line arguments
    case "$1" in
        quick)
            echo -e "${YELLOW}Running quick tests (no coverage)...${NC}"
            pytest -v
            ;;
        
        coverage)
            echo -e "${YELLOW}Running tests with detailed coverage...${NC}"
            pytest --cov=src --cov-report=term-missing --cov-report=html
            echo -e "${GREEN}📊 Open htmlcov/index.html to view report${NC}"
            ;;
        
        watch)
            echo -e "${YELLOW}Running in watch mode...${NC}"
            if command -v ptw &> /dev/null; then
                ptw
            else
                echo -e "${RED}pytest-watch not installed${NC}"
                echo "Install: pip install pytest-watch"
                exit 1
            fi
            ;;
        
        parallel)
            echo -e "${YELLOW}Running tests in parallel...${NC}"
            if command -v pytest-xdist &> /dev/null; then
                pytest -n auto --cov=src
            else
                echo -e "${RED}pytest-xdist not installed${NC}"
                echo "Install: pip install pytest-xdist"
                exit 1
            fi
            ;;
        
        lint)
            echo -e "${YELLOW}Running code quality checks...${NC}"
            echo "→ Flake8..."
            flake8 src tests --count --max-line-length=120 --statistics || true
            echo "→ Black..."
            black --check src tests || true
            echo "→ Isort..."
            isort --check-only src tests || true
            ;;
        
        fix)
            echo -e "${YELLOW}Auto-fixing code formatting...${NC}"
            black src tests
            isort src tests
            echo -e "${GREEN}✅ Code formatted${NC}"
            ;;
        
        clean)
            echo -e "${YELLOW}Cleaning test artifacts...${NC}"
            rm -rf .pytest_cache .coverage htmlcov coverage.xml
            find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
            echo -e "${GREEN}✅ Cleaned${NC}"
            ;;
        
        *)
            echo "Usage: ./run_tests.sh [command]"
            echo ""
            echo "Commands:"
            echo "  (none)     Run all tests with coverage (default)"
            echo "  quick      Run tests without coverage"
            echo "  coverage   Run tests with detailed coverage report"
            echo "  watch      Run tests in watch mode"
            echo "  parallel   Run tests in parallel"
            echo "  lint       Run code quality checks"
            echo "  fix        Auto-fix code formatting"
            echo "  clean      Remove test artifacts"
            exit 1
            ;;
    esac
fi

exit 0
