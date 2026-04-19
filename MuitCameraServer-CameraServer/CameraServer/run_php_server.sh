#!/bin/bash
# Start mock PHP server for testing

echo "Starting mock PHP server..."
echo "Server will run on: http://127.0.0.1:8080"
echo ""
echo "Endpoints:"
echo "  - POST /api/find_auditory.php"
echo "  - POST /api/cabinet_answer.php"
echo ""
echo "Press Ctrl+C to stop"
echo ""

php -S 127.0.0.1:8080
