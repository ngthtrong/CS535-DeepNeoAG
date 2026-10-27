"""Reader-facing model names; machine identifiers remain in raw evidence."""
import re

MODEL_NAMES = {
    "M0": "Composition + LR",
    "M1": "One-hot + MCNN",
    "M2": "ESM 8M + pooled LR",
    "M3": "ESM 8M + CNN",
    "M4": "ESM 8M + MCNN",
    "M5": "ESM 35M + pooled LR",
    "M6": "ESM 35M + CNN",
    "M7": "ESM 35M + MCNN",
}


def readable_text(text):
    """Rename visible prose/table labels while preserving Markdown URL targets."""
    targets = []
    def protect(match):
        targets.append(match.group(0))
        return f"@@LINKTARGET{len(targets)-1}@@"
    text = re.sub(r"\]\([^\n)]*\)", protect, text)
    text = re.sub(r"\b(M[0-7])_([a-f0-9]{10})\b",
                  lambda m: f"{MODEL_NAMES[m[1]]} [config {m[2]}]", text)
    text = re.sub(r"\bM[0-7]\b", lambda m: MODEL_NAMES[m[0]], text)
    for i, target in enumerate(targets):
        text = text.replace(f"@@LINKTARGET{i}@@", target)
    return text
