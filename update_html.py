import re

with open("sfm-blockly-editor.html", "r") as f:
    content = f.read()

with open("heuristic_fix.js", "r") as f:
    new_func = f.read()

# Escaping backslashes for re.sub replacement string
repl = new_func.replace("\\", "\\\\") + "\n\nfunction importSFM()"

pattern = r"function heuristicParseSFM\(text\)\{.*?\}\n\nfunction importSFM\(\)"
content = re.sub(pattern, repl, content, flags=re.DOTALL)

with open("sfm-blockly-editor.html", "w") as f:
    f.write(content)
