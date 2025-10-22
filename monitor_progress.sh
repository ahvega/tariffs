#!/bin/bash
while true; do
  if [ -f "logs/keyword_generation_deepseek.log" ]; then
    COUNT=$(grep -c "Keywords generados:" logs/keyword_generation_deepseek.log 2>/dev/null || echo "0")
    PERCENT=$(echo "scale=1; ($COUNT / 7524) * 100" | bc 2>/dev/null || echo "0")
    echo "[$(date +%H:%M:%S)] Progress: $COUNT/7524 ($PERCENT%)"
    
    # Check if process is complete
    if grep -q "Proceso completado" logs/keyword_generation_deepseek.log 2>/dev/null; then
      echo "=== REGENERATION COMPLETE ==="
      break
    fi
  fi
  sleep 300  # Check every 5 minutes
done
