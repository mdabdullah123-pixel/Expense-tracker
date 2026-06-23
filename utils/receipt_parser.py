"""
Receipt Scanner/Parser - Extracts structured data from receipt images.

Uses OCR (Tesseract) for text extraction from images with graceful fallback.
Processes extracted text to identify merchant names, dates, amounts, and line items.
Supports common receipt formats and falls back to AI-based parsing when needed.
"""

import contextlib
import io
import logging
import re
from datetime import datetime

from PIL import Image

logger = logging.getLogger(__name__)


class ReceiptParser:
    """
    Parser for extracting structured information from receipt images.

    1. Extracts text from images using OCR (Tesseract)
    2. Falls back gracefully if OCR is unavailable
    3. Identifies merchant, date, total, and items from text
    """

    def __init__(self, tesseract_cmd: str | None = None):
        """
        Initialize the receipt parser.

        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        self.tesseract_cmd = tesseract_cmd
        self._tesseract_available: bool | None = None

    def _check_tesseract(self) -> bool:
        """
        Check if Tesseract OCR is available.

        Returns:
            True if tesseract is available
        """
        if self._tesseract_available is not None:
            return self._tesseract_available

        try:
            import pytesseract

            if self.tesseract_cmd:
                pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

            # Try to get tesseract version
            version = pytesseract.get_tesseract_version()
            self._tesseract_available = version is not None
            if self._tesseract_available:
                logger.info("Tesseract OCR available: %s", version)
            return self._tesseract_available

        except Exception as e:
            logger.warning("Tesseract OCR not available: %s", str(e))
            self._tesseract_available = False
            return False

    def extract_text_from_image(self, image_bytes: bytes) -> str | None:
        """
        Extract text from a receipt image using OCR.

        Args:
            image_bytes: Raw image bytes

        Returns:
            Extracted text or None on failure
        """
        if not self._check_tesseract():
            logger.warning("OCR not available, cannot extract text")
            return None

        try:
            import pytesseract

            # Open image from bytes
            image = Image.open(io.BytesIO(image_bytes))

            # Preprocess image for better OCR
            grayscale_image = image.convert("L")  # Convert to grayscale

            # Extract text
            text = pytesseract.image_to_string(grayscale_image, lang="eng")

            if text and text.strip():
                logger.info("Successfully extracted text from receipt image")
                return text.strip()
            else:
                logger.warning("No text found in receipt image")
                return None

        except ImportError:
            logger.error("pytesseract package not installed")
            return None
        except Exception as e:
            logger.error("Failed to extract text from image: %s", str(e))
            return None

    def parse_receipt_text(self, text: str) -> dict:
        """
        Parse raw receipt text to extract structured information.

        Uses regex patterns and heuristics for extraction.

        Args:
            text: Raw text from receipt

        Returns:
            Dict with merchant, date, total, items, category_suggestion
        """
        if not text:
            return {
                "merchant": None,
                "date": None,
                "total": None,
                "items": [],
                "category_suggestion": "Other",
            }

        result = {
            "merchant": self._extract_merchant(text),
            "date": self._extract_date(text),
            "total": self._extract_total(text),
            "items": self._extract_items(text),
            "category_suggestion": self._suggest_category(text),
        }

        logger.info(
            "Receipt parsed: merchant=%s, total=%s", result["merchant"], result["total"]
        )
        return result

    def _extract_merchant(self, text: str) -> str | None:
        """
        Extract merchant/store name from receipt text.

        Usually the first few lines of a receipt.

        Args:
            text: Receipt text

        Returns:
            Merchant name or None
        """
        lines = text.strip().split("\n")

        # Take first non-empty line as merchant
        for line in lines:
            line = line.strip()
            if (
                line
                and len(line) > 2
                and len(line) < 100
                and not re.search(r"\d{2}[/\-\.]\d{2}[/\-\.]\d{2,4}", line)
                and not re.search(r"total|amount|bill|receipt|tax|gst", line.lower())
            ):
                return line.strip()

        return None

    def _extract_date(self, text: str) -> str | None:
        """
        Extract date from receipt text.

        Args:
            text: Receipt text

        Returns:
            Date string in YYYY-MM-DD format or None
        """
        # Common date patterns
        patterns = [
            r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{4})",  # DD/MM/YYYY
            r"(\d{4}[/\-\.]\d{2}[/\-\.]\d{2})",  # YYYY/MM/DD
            r"(\d{2}[/\-\.]\d{2}[/\-\.]\d{2})",  # DD/MM/YY
            r"(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})",  # DD Mon YYYY
            r"((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})",  # Mon DD, YYYY
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1)
                # Try to parse and standardize
                try:
                    for fmt in [
                        "%d/%m/%Y",
                        "%d-%m-%Y",
                        "%Y/%m/%d",
                        "%Y-%m-%d",
                        "%d/%m/%y",
                        "%d-%m-%y",
                        "%d %b %Y",
                        "%d %B %Y",
                        "%b %d, %Y",
                        "%B %d, %Y",
                    ]:
                        try:
                            dt = datetime.strptime(date_str, fmt)
                            return dt.strftime("%Y-%m-%d")
                        except ValueError:
                            continue
                except Exception:
                    pass

        return None

    def _extract_total(self, text: str) -> float | None:
        """
        Extract total amount from receipt text.

        Args:
            text: Receipt text

        Returns:
            Total amount or None
        """
        # Look for total patterns
        patterns = [
            r"(?:total|amount|due|grand\s*total|net)\s*:?\s*[₹$€£]?\s*(\d+\.?\d*)",
            r"[₹$€£]\s*(\d+\.\d{2})\s*$",
            r"[₹$€£]\s*(\d+\.\d{2})\s*(?:total|only)",
        ]

        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for m in matches:
                with contextlib.suppress(ValueError):
                    amounts.append(float(m))

        if amounts:
            # Return the largest amount (usually the total)
            return max(amounts)

        # Fallback: find any currency amount
        fallback = re.findall(r"[₹$€£]\s*(\d+\.?\d*)", text)
        if fallback:
            try:
                return max(float(f) for f in fallback)
            except ValueError:
                pass

        return None

    def _extract_items(self, text: str) -> list:
        """
        Extract line items from receipt text.

        Args:
            text: Receipt text

        Returns:
            List of item descriptions
        """
        lines = text.strip().split("\n")
        items = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header/footer lines
            if re.search(
                r"(total|subtotal|tax|gst|vat|change|cash|card|upi|receipt|thank)",
                line.lower(),
            ):
                continue

            # Skip date and address lines
            if re.search(r"\d{2}[/\-\.]\d{2}[/\-\.]\d{2,4}", line):
                continue

            # Skip purely numeric lines
            if re.match(r"^[\d\s\.\,₹$€£]+$", line):
                continue

            # Lines with item description (and optionally price)
            if len(line) > 3 and not line.startswith(("#", "*", "-")):
                # Remove price from the end if present
                item = re.sub(r"\s+\d+\.?\d*\s*$", "", line)
                item = re.sub(r"^[₹$€£]\s*\d+\.?\d*\s*", "", item)
                item = item.strip()

                if item and len(item) > 2 and item not in items:
                    items.append(item)

        return items[:20]  # Limit to 20 items

    def _suggest_category(self, text: str) -> str:
        """
        Suggest an expense category based on receipt content.

        Args:
            text: Receipt text

        Returns:
            Suggested category
        """
        text_lower = text.lower()

        category_keywords = {
            "Food": [
                "restaurant",
                "cafe",
                "food",
                "dining",
                "pizza",
                "burger",
                "swiggy",
                "zomato",
                "grocery",
                "supermarket",
                "bakery",
                "meal",
            ],
            "Transport": [
                "uber",
                "ola",
                "taxi",
                "cab",
                "fuel",
                "petrol",
                "diesel",
                "metro",
                "bus",
                "train",
                "parking",
                "toll",
            ],
            "Shopping": [
                "mall",
                "store",
                "retail",
                "clothing",
                "apparel",
                "amazon",
                "flipkart",
                "electronics",
                "furniture",
            ],
            "Entertainment": [
                "movie",
                "cinema",
                "theatre",
                "netflix",
                "spotify",
                "game",
                "concert",
                "ticket",
            ],
            "Health": [
                "hospital",
                "clinic",
                "pharmacy",
                "medical",
                "doctor",
                "medicine",
                "health",
                "fitness",
                "gym",
            ],
            "Education": [
                "school",
                "college",
                "university",
                "course",
                "book",
                "training",
                "tution",
                "class",
            ],
            "Bills": [
                "electricity",
                "water",
                "gas",
                "internet",
                "phone",
                "mobile",
                "broadband",
                "subscription",
            ],
        }

        scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=lambda x: scores[x])

        return "Other"
