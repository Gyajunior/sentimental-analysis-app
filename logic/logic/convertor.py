cat << 'EOF' > logic/converter.py
import re
from config import MODERN_TO_ARCHAIC, ETH_VERBS

def convert_to_shakespearean(text: str) -> str:
    result = text

    for pattern, replacement in MODERN_TO_ARCHAIC:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    for verb in ETH_VERBS:
        result = re.sub(
            r'\bhe ' + verb + r's?\b',
            f'he {verb}eth',
            result, flags=re.IGNORECASE
        )
        result = re.sub(
            r'\bshe ' + verb + r's?\b',
            f'she {verb}eth',
            result, flags=re.IGNORECASE
        )

    sentences = re.split(r'(?<=[.!?])\s+', result)
    result = ' '.join(s[:1].upper() + s[1:] if s else s for s in sentences)

    result = result.strip()
    if result and result[-1] not in '.!?':
        result += '.'

    return result
EOF