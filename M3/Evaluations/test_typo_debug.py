import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(parent_dir))

from components.entity_extractor import EntityExtractor

extractor = EntityExtractor(debug=True)
print("Testing typo validation...")
result = extractor._find_closest_match_with_llm('Paaris', extractor.VALID_CITIES, 'city')
print(f'\n\nFinal Result: {result}')
