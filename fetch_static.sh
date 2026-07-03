#!/bin/bash
# Builds the static/ directory by downloading third-party CSS/JS from CDN
# and creating stub files for project-specific assets.
# Run: bash fetch_static.sh  (from the pythonfiddle-modernize root)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S="$SCRIPT_DIR/static"

echo "==> Creating directory structure..."
mkdir -p "$S/css/codemirror/util"
mkdir -p "$S/js/build/lib"
mkdir -p "$S/js/codemirror/mode/python"
mkdir -p "$S/images"

# ── CSS: third-party ────────────────────────────────────────────────────────
echo "==> Downloading CSS..."
_dl() { curl -fsSL --retry 2 --retry-delay 1 -o "$1" "$2" && echo "    OK: $2" || echo "    WARN: failed $2"; }

_dl "$S/css/jquery-ui.cupertino.css" \
  "https://code.jquery.com/ui/1.12.1/themes/cupertino/jquery-ui.min.css"

_dl "$S/css/codemirror.css" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.css"

_dl "$S/css/codemirror/util/dialog.css" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/dialog/dialog.min.css"

_dl "$S/css/show-hint.css" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/hint/show-hint.min.css"

# Ensure CSS files exist (create empty stubs if downloads failed)
[ -s "$S/css/jquery-ui.cupertino.css" ] || echo "/* jquery-ui cupertino stub */" > "$S/css/jquery-ui.cupertino.css"
[ -s "$S/css/codemirror.css" ] || echo "/* codemirror stub */" > "$S/css/codemirror.css"
[ -s "$S/css/codemirror/util/dialog.css" ] || echo "/* codemirror dialog stub */" > "$S/css/codemirror/util/dialog.css"
[ -s "$S/css/show-hint.css" ] || echo "/* show-hint stub */" > "$S/css/show-hint.css"

# ── CSS: project stubs ──────────────────────────────────────────────────────
cat > "$S/css/layout-default.css" << 'EOF'
/* jQuery Layout default styles (stub) */
.ui-layout-pane { position: absolute; z-index: 0; overflow: auto; }
.ui-layout-resizer { position: absolute; z-index: 1; font-size: 1px; }
.ui-layout-toggler { position: absolute; z-index: 2; }
EOF

cat > "$S/css/boilerplate.css" << 'EOF'
/* HTML5 Boilerplate (stub) */
*, *::before, *::after { box-sizing: border-box; }
html { font-size: 100%; -webkit-text-size-adjust: 100%; }
body { margin: 0; font-size: 13px; line-height: 1.231; }
EOF

cat > "$S/css/style.css" << 'EOF'
/* PythonFiddle main styles (stub — fill in from original or redesign) */
body { font-family: Arial, sans-serif; background: #f5f5f5; }
#logo { float: right; text-align: center; }
#logo h1 { margin: 0; font-size: 1.4em; color: #3a3a3a; }
#logo h3 { margin: 0; font-size: 0.8em; color: #777; }
EOF

cat > "$S/css/python.css" << 'EOF'
/* PythonFiddle Python-specific styles (stub) */
.CodeMirror { height: auto; border: 1px solid #ddd; font-size: 13px; }
EOF

cat > "$S/css/faq.css" << 'EOF'
/* PythonFiddle FAQ styles (stub) */
EOF

# ── CSS bundle: styles.python.css ──────────────────────────────────────────
echo "==> Building css/styles.python.css bundle..."
cat \
  "$S/css/jquery-ui.cupertino.css" \
  "$S/css/layout-default.css" \
  "$S/css/boilerplate.css" \
  "$S/css/codemirror.css" \
  "$S/css/codemirror/util/dialog.css" \
  "$S/css/show-hint.css" \
  "$S/css/style.css" \
  "$S/css/python.css" \
  "$S/css/faq.css" \
  > "$S/css/styles.python.css"
echo "    css/styles.python.css: $(wc -c < "$S/css/styles.python.css") bytes"

# ── CSS: other bundles ──────────────────────────────────────────────────────
echo "/* login styles stub */" > "$S/css/login.css"
echo "/* snippets styles stub */" > "$S/css/user.css"
cat "$S/css/user.css" > "$S/css/snippets.css"

# ── JS: CDN downloads (failures are non-fatal; stubs cover gaps) ────────────
echo "==> Downloading JS (failures are non-fatal)..."

_dl() { curl -fsSL --retry 2 --retry-delay 1 -o "$1" "$2" && echo "    OK: $2" || echo "    WARN: failed $2 — stub will be used"; }

_dl "$S/js/jquery.js" \
  "https://code.jquery.com/jquery-1.12.4.min.js"

_dl "$S/js/build/lib/jquery-ui.python.min.js" \
  "https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"

_dl "$S/js/build/lib/sugar.min.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/sugar/2.0.6/sugar.min.js"

_dl "$S/js/underscore.js" \
  "https://cdn.jsdelivr.net/npm/underscore@1.13.6/underscore-min.js"

_dl "$S/js/knockout-latest.debug.js" \
  "https://cdn.jsdelivr.net/npm/knockout@3.5.1/build/output/knockout-latest.js"

_dl "$S/js/knockout.mapping.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/knockout.mapping/2.4.1/knockout.mapping.min.js"

_dl "$S/js/jquery.validate.js" \
  "https://cdn.jsdelivr.net/npm/jquery-validation@1.20.0/dist/jquery.validate.min.js"

_dl "$S/js/codemirror.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/codemirror.min.js"

_dl "$S/js/codemirror/mode/python/python.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/mode/python/python.min.js"

_dl "$S/js/codemirror/show-hint.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/hint/show-hint.min.js"

_dl "$S/js/codemirror/dialog.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/dialog/dialog.min.js"

_dl "$S/js/codemirror/searchcursor.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/search/searchcursor.min.js"

_dl "$S/js/codemirror/search.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/search/search.min.js"

_dl "$S/js/codemirror/match-highlighter.js" \
  "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16/addon/search/match-highlighter.min.js"

# Ensure show-hint exists before copying to python-hint
[ -s "$S/js/codemirror/show-hint.js" ] && cp "$S/js/codemirror/show-hint.js" "$S/js/codemirror/python-hint.js" || echo "/* python-hint stub */" > "$S/js/codemirror/python-hint.js"

# ── JS: project-specific stubs ──────────────────────────────────────────────
echo "==> Creating project-specific JS stubs..."

# jquery.layout stub
cat > "$S/js/build/lib/jquery.layout.min.js" << 'EOF'
/* jQuery Layout stub — install jquery-layout npm package to replace */
EOF

for f in \
  layout.js \
  additional-methods.js \
  knockout-jquery-ui-widget.js \
  bindings.js \
  bowser.js \
  classy.js \
  json.js \
  store.js \
  base64.js \
  modules.js \
  helpers.js \
  trie.js \
  autocomplete.js \
  "date.format.js" \
  "python-configuration.js" \
  navigation.js \
  fiddle.js \
  "xd-yql.js" \
  ZeroClipboard.js \
  setupClipboard.js \
  examples.js \
  "packages.python.js" \
  "jquery-ui.tag-complete.js" \
  "jquery.csrf.js" \
  "jquery.history.js"
do
  echo "/* $f stub */" > "$S/js/$f"
done

mkdir -p "$S/js/compiled-coffee"
for f in model.js "engine.require.js" "python-engine.js"; do
  echo "/* compiled-coffee/$f stub */" > "$S/js/compiled-coffee/$f"
done

# ── JS bundles ───────────────────────────────────────────────────────────────
echo "==> Building JS bundles..."

cat \
  "$S/js/build/lib/jquery-ui.python.min.js" \
  "$S/js/build/lib/jquery.layout.min.js" \
  "$S/js/layout.js" \
  > "$S/js/jquery-ui.python.js"

cat \
  "$S/js/jquery.validate.js" \
  "$S/js/additional-methods.js" \
  "$S/js/knockout-latest.debug.js" \
  "$S/js/knockout-jquery-ui-widget.js" \
  "$S/js/knockout.mapping.js" \
  "$S/js/bindings.js" \
  > "$S/js/knockout.js"

cat \
  "$S/js/codemirror.js" \
  "$S/js/codemirror/show-hint.js" \
  "$S/js/codemirror/python-hint.js" \
  "$S/js/codemirror/mode/python/python.js" \
  "$S/js/codemirror/match-highlighter.js" \
  "$S/js/codemirror/dialog.js" \
  "$S/js/codemirror/searchcursor.js" \
  "$S/js/codemirror/search.js" \
  > "$S/js/codemirror.python.js"

cat \
  "$S/js/jquery-ui.tag-complete.js" \
  "$S/js/jquery.csrf.js" \
  "$S/js/jquery.history.js" \
  "$S/js/compiled-coffee/model.js" \
  > "$S/js/python.editor.js"

cat \
  "$S/js/fiddle.js" \
  "$S/js/xd-yql.js" \
  "$S/js/ZeroClipboard.js" \
  "$S/js/setupClipboard.js" \
  "$S/js/base64.js" \
  "$S/js/examples.js" \
  "$S/js/packages.python.js" \
  > "$S/js/python.init.js"

cat \
  "$S/js/bowser.js" \
  "$S/js/underscore.js" \
  "$S/js/build/lib/sugar.min.js" \
  "$S/js/classy.js" \
  "$S/js/json.js" \
  "$S/js/store.js" \
  "$S/js/base64.js" \
  "$S/js/modules.js" \
  "$S/js/helpers.js" \
  "$S/js/trie.js" \
  "$S/js/autocomplete.js" \
  "$S/js/date.format.js" \
  "$S/js/python-configuration.js" \
  "$S/js/compiled-coffee/engine.require.js" \
  "$S/js/compiled-coffee/python-engine.js" \
  > "$S/js/python.bootstrap.js"

# ── Images ───────────────────────────────────────────────────────────────────
echo "==> Creating image placeholder..."
# Minimal 1x1 transparent PNG (base64-decoded)
python3 -c "
import base64, sys
# 1x1 transparent PNG
data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=='
sys.stdout.buffer.write(base64.b64decode(data))
" > "$S/images/Python_Fiddler.png"

echo ""
echo "=== Static files created ==="
echo "CSS bundle: $(wc -c < "$S/css/styles.python.css") bytes"
echo "JS files: $(find "$S/js" -name '*.js' | wc -l) files"
echo "Image: $(ls -lh "$S/images/Python_Fiddler.png" | awk '{print $5}')"
