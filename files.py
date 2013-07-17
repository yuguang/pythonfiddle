import sys

command = sys.argv[1]
if command == 'syncmedia':
    build_config = True
else:
    build_config = False

if not build_config:
    FILES = {
        'BOWSER': 'js/bowser.js',
        'UNDERSCORE': 'js/underscore.js',
        'VALIDATE': 'js/jquery.validate.js',
        'KNOCKOUT': 'js/knockout-latest.debug.js',
        'KNOCKOUT_MAPPING': 'js/knockout.mapping.js',
    }
else:
    FILES = {
        'BOWSER': 'js/build/lib/bowser.min.js',
        'UNDERSCORE': 'js/build/lib/underscore.min.js',
        'VALIDATE': 'js/build/lib/jquery.validate.min.js',
        'KNOCKOUT': 'js/build/lib/knockout.min.js',
        'KNOCKOUT_MAPPING': 'js/build/lib/knockout.mapping.min.js',
    }

# Media files
MEDIASYNC_JOINED = {
    'css/boilerplate.css': [
        'css/boilerplate.css'
    ],
    'css/snippets.css': [
        'css/user.css'
    ],
    'css/login.css': [
        'css/login.css'
    ],
    'css/styles.python.css': [
        'css/jquery-ui.cupertino.css',
        'css/layout-default.css',
        'css/boilerplate.css',
        'css/codemirror.css',
        'css/codemirror/util/dialog.css',
        'css/show-hint.css',
        'css/style.css',
        'css/python.css',
        'css/faq.css'
    ],
    'js/navigation.js': [
        'js/navigation.js'
    ],
    'js/jquery-ui.python.js': [
        'js/build/lib/jquery-ui.python.min.js',
        'js/build/lib/jquery.layout.min.js',
        'js/layout.js',
    ],
    'js/knockout.js': [
        FILES['VALIDATE'],
        'js/additional-methods.js',
        FILES['KNOCKOUT'],
        'js/knockout-jquery-ui-widget.js',
        FILES['KNOCKOUT_MAPPING'],
        'js/bindings.js',
    ],
    'js/codemirror.python.js': [
        'js/codemirror.js',
        'js/codemirror/show-hint.js',
        'js/codemirror/python-hint.js',
        'js/codemirror/mode/python/python.js',
        'js/codemirror/match-highlighter.js',
        'js/codemirror/dialog.js',
        'js/codemirror/searchcursor.js',
        'js/codemirror/search.js',
    ],
    'js/python.editor.js': [
        'js/jquery.csrf.js',
        'js/jquery.history.js',
        'js/compiled-coffee/model.js',
    ],
    'js/python.init.js': [
        'js/fiddle.js',
        'js/xd-yql.js',
        'js/ZeroClipboard.js',
        'js/setupClipboard.js',
        'js/base64.js',
        'js/examples.js',
        'js/packages.python.js',
    ],
    'js/python.bootstrap.js': [
        FILES['BOWSER'],
        FILES['UNDERSCORE'],
        'js/classy.js',
        'js/json.js',
        'js/store.js',
        'js/base64.js',
        'js/modules.js',
        'js/helpers.js',
        'js/trie.js',
        'js/autocomplete.js',
        'js/date.format.js',
        'js/python-configuration.js',
        'js/compiled-coffee/engine.require.js',
        'js/compiled-coffee/python-engine.js',
    ]
}

