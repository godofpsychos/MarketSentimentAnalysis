#!/bin/bash

# Cursor appearance utility script

case "$1" in
    "block")
        echo -e "\e[2 q"  # Block cursor
        echo "Cursor changed to block"
        ;;
    "blink")
        echo -e "\e[5 q"  # Blinking block cursor
        echo "Cursor changed to blinking block"
        ;;
    "line")
        echo -e "\e[6 q"  # Blinking line cursor
        echo "Cursor changed to blinking line"
        ;;
    "steady")
        echo -e "\e[3 q"  # Steady block cursor
        echo "Cursor changed to steady block"
        ;;
    *)
        echo "Usage: $0 {block|blink|line|steady}"
        echo "  block  - Block cursor"
        echo "  blink  - Blinking block cursor"
        echo "  line   - Blinking line cursor"
        echo "  steady - Steady block cursor"
        ;;
esac 