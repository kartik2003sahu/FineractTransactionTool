#!/bin/bash

echo "========================================"
echo "Switch Fineract Configuration"
echo "========================================"
echo ""
echo "Available configurations:"
echo "1. Production (.env.production)"
echo "2. Staging (.env.staging)"
echo "3. Development (.env.development)"
echo "4. Custom (.env)"
echo ""
read -p "Select configuration (1-4): " choice

case $choice in
    1)
        cp -f .env.production .env
        echo "Switched to PRODUCTION configuration"
        ;;
    2)
        cp -f .env.staging .env
        echo "Switched to STAGING configuration"
        ;;
    3)
        cp -f .env.development .env
        echo "Switched to DEVELOPMENT configuration"
        ;;
    4)
        echo "Using CUSTOM configuration (.env)"
        ;;
    *)
        echo "Invalid choice!"
        exit 1
        ;;
esac

echo ""
echo "Configuration active. Restart the tool for changes to take effect."
echo ""
