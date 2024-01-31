apt-get install poppler-utils
apt-get install tesseract-ocr

from typing import Any

from pydantic import BaseModel
from unstructured partition.pdf import partition_pdf #this function wil help in partitioning the pdf file into individual elements

# fetche elements from the pdf file

def fetch_elements(filename_path):
    raw_pdf_elements = partition_pdf(
        filename_path,
        # Using pdf format to find embedded image blocks
        extract_images_in_pdf=True,
        # Use layout model (YOLOX) to get bounding boxes (for tables) and find titles
        # Titles are any sub-section of the document
        infer_table_structure=True,
        # Post processing to aggregate text once we have the title
        chunking_strategy="by_title",
        # Chunking params to aggregate text blocks
        # Attempt to create a new chunk 3800 chars
        # Attempt to keep chunks > 2000 chars
        # Hard max on chunks
        max_characters=4000,
        new_after_n_chars=3800,
        combine_text_under_n_chars=2000,
        image_output_dir_path="/content/",
    )
    return raw_pdf_elements

def element_wise_count(raw_pdf_elements):
    category_counts = {}

    for element in raw_pdf_elements:
        category = str(type(element))
        if category in category_counts:
            category_counts[category] += 1
        else:
            category_counts[category] = 1

    # Unique_categories will have unique elements
    # TableChunk if Table > max chars set above
    unique_categories = set(category_counts.keys())
    print(category_counts)


class Element(BaseModel):
    type: str
    text: Any


def num_elements(raw_pdf_elements):
    # Categorize by type
    categorized_elements = []
    for element in raw_pdf_elements:
        if "unstructured.documents.elements.Table" in str(type(element)):
            categorized_elements.append(Element(type="table", text=str(element)))
        elif "unstructured.documents.elements.CompositeElement" in str(type(element)):
            categorized_elements.append(Element(type="text", text=str(element)))

    # Tables
    table_elements = [e for e in categorized_elements if e.type == "table"]
    print('Number of tables:', len(table_elements))

    # Text
    text_elements = [e for e in categorized_elements if e.type == "text"]
    print('Number of text elements"', len(text_elements))