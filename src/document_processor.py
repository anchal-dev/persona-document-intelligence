import os
import json
from pathlib import Path
from typing import List, Dict, Any
import PyPDF2
import re
from datetime import datetime

class DocumentProcessor:
    """
    Handles PDF document processing, text extraction, and metadata collection.
    """
    
    def __init__(self, input_folder: str = "data/input", output_folder: str = "data/output"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
    def find_pdf_files(self) -> List[Path]:
        """Find all PDF files in the input directory."""
        pdf_files = list(self.input_folder.glob("*.pdf"))
        return sorted(pdf_files)
    
    def extract_text_from_pdf(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Extract text content from a PDF file.
        Returns a dictionary with filename, content, and metadata.
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract metadata
                metadata = {
                    'filename': pdf_path.name,
                    'file_size': pdf_path.stat().st_size,
                    'num_pages': len(pdf_reader.pages),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    'processed_at': datetime.now().isoformat()
                }
                
                # Extract text from all pages
                text_content = ""
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    except Exception as e:
                        print(f"Warning: Could not extract text from page {page_num + 1} of {pdf_path.name}: {e}")
                
                # Clean and structure the text
                cleaned_text = self.clean_text(text_content)
                
                return {
                    'metadata': metadata,
                    'content': cleaned_text,
                    'raw_content': text_content,
                    'word_count': len(cleaned_text.split()),
                    'sections': self.identify_sections(cleaned_text)
                }
                
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")
            return {
                'metadata': {'filename': pdf_path.name, 'error': str(e)},
                'content': "",
                'raw_content': "",
                'word_count': 0,
                'sections': []
            }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Remove page headers/footers that might be repetitive
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 3:  # Skip very short lines that might be artifacts
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def identify_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        Identify potential sections in the document based on formatting patterns.
        """
        sections = []
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Check if line might be a heading (all caps, short, followed by content)
            if (line.isupper() and len(line) < 100 and len(line) > 3) or \
               (line.endswith(':') and len(line) < 80) or \
               (re.match(r'^[A-Z][A-Za-z\s]+$', line) and len(line) < 60):
                
                # Save previous section
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line,
                    'content': '',
                    'start_line': i,
                    'word_count': 0
                }
            elif current_section:
                current_section['content'] += line + ' '
                current_section['word_count'] = len(current_section['content'].split())
        
        # Add the last section
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def process_all_documents(self) -> List[Dict[str, Any]]:
        """
        Process all PDF files in the input directory.
        Returns a list of processed document dictionaries.
        """
        pdf_files = self.find_pdf_files()
        processed_docs = []
        
        print(f"Found {len(pdf_files)} PDF files to process...")
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            doc_data = self.extract_text_from_pdf(pdf_file)
            processed_docs.append(doc_data)
        
        # Save processed documents
        self.save_processed_documents(processed_docs)
        
        return processed_docs
    
    def save_processed_documents(self, documents: List[Dict[str, Any]]):
        """Save processed documents to JSON file."""
        output_file = self.output_folder / "processed_documents.json"
        
        # Create a summary for saving
        save_data = {
            'processing_timestamp': datetime.now().isoformat(),
            'total_documents': len(documents),
            'documents': documents
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"Processed documents saved to: {output_file}")
    
    def get_collection_summary(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a summary of the entire document collection."""
        total_words = sum(doc.get('word_count', 0) for doc in documents)
        total_pages = sum(doc.get('metadata', {}).get('num_pages', 0) for doc in documents)
        
        # Get all section titles across documents
        all_sections = []
        for doc in documents:
            sections = doc.get('sections', [])
            all_sections.extend([s['title'] for s in sections])
        
        return {
            'total_documents': len(documents),
            'total_pages': total_pages,
            'total_words': total_words,
            'average_words_per_doc': total_words / len(documents) if documents else 0,
            'all_section_titles': all_sections,
            'document_topics': self.extract_key_topics(documents)
        }
    
    def extract_key_topics(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Extract key topics from document collection using simple keyword analysis."""
        all_text = " ".join([doc.get('content', '') for doc in documents])
        
        # Simple keyword extraction (you could enhance this with NLP libraries)
        words = re.findall(r'\b[A-Za-z]{4,}\b', all_text.lower())
        word_freq = {}
        
        # Common stop words to exclude
        stop_words = {'that', 'this', 'with', 'from', 'they', 'have', 'been', 'were', 'said', 'each', 
                     'which', 'their', 'will', 'about', 'there', 'could', 'other', 'after', 'first',
                     'also', 'back', 'into', 'here', 'how', 'then', 'them', 'these', 'many', 'some',
                     'what', 'would', 'make', 'like', 'time', 'very', 'when', 'come', 'its', 'now',
                     'over', 'just', 'his', 'has', 'had', 'up', 'her', 'out', 'my', 'she', 'or',
                     'an', 'a', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'if', 'in', 'is', 
                     'it', 'no', 'not', 'of', 'on', 'such', 'the', 'to', 'was', 'we', 'you'}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
        return [word for word, freq in top_keywords]