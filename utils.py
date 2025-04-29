import pytesseract
import re
from PIL import Image

def extract_lab_tests(image: Image.Image):
    # Preprocess the image (convert to grayscale and threshold)
    image = image.convert("L")
    image = image.point(lambda x: 0 if x < 140 else 255)

    # OCR
    text = pytesseract.image_to_string(image)

    # Debug print
    print("\n=== OCR OUTPUT ===\n", text)

    # Clean up and split lines
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    test_data = []

    # Relaxed regex for test extraction
    pattern = re.compile(
        r"(?P<name>[A-Z \(\)]+)\s+(?P<value>\d+\.?\d*)\s*(?P<unit>[a-zA-Z/%]+)?\s*(?:\(?\s*(?P<range>\d+\.?\d*)\s*-\s*(?P<range_high>\d+\.?\d*)\)?)?",
        re.IGNORECASE
    )

    for line in lines:
        match = pattern.search(line)
        if match:
            test_name = match.group("name").strip()
            test_value = float(match.group("value"))
            test_unit = match.group("unit") or ""
            ref_low = match.group("range")
            ref_high = match.group("range_high")

            if ref_low and ref_high:
                ref_low = float(ref_low)
                ref_high = float(ref_high)
                out_of_range = not (ref_low <= test_value <= ref_high)
                bio_range = f"{ref_low}-{ref_high}"
            else:
                out_of_range = False
                bio_range = ""

            test_data.append({
                "test_name": test_name,
                "test_value": str(test_value),
                "bio_reference_range": bio_range,
                "test_unit": test_unit,
                "lab_test_out_of_range": out_of_range
            })

    return test_data