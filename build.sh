#!/bin/bash
# ══════════════════════════════════════════════
#  build.sh — ricompone nisyros.html dai componenti
#  Uso: ./build.sh
# ══════════════════════════════════════════════

OUT="nisyros.html"

cat \
  sections/head.html \
  sections/nav.html \
  sections/manifesto.html \
  sections/hero.html \
  sections/wines.html \
  sections/faces.html \
  sections/contact.html \
  > "$OUT.tmp"

# Aggiunge il tag <script> con main.js e chiude body/html
cat >> "$OUT.tmp" << 'EOF'

<script>
EOF

cat js/main.js >> "$OUT.tmp"

cat >> "$OUT.tmp" << 'EOF'
</script>
</body>
</html>
EOF

mv "$OUT.tmp" "$OUT"
echo "✓ Build completato → $OUT"
