import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from document_processor import DocumentProcessor
from persona_analyzer import PersonaAnalyzer

class PersonaDocumentIntelligenceSystem:
    """
    Main system that coordinates document processing and persona-driven analysis.
    Handles input/output in the format expected by the challenge system.
    """
    
    def __init__(self, input_folder: str = "data/input", output_folder: str = "data/output"):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        self.document_processor = DocumentProcessor(input_folder, output_folder)
        
    def process_challenge_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input in the challenge format and return structured output.
        """
        # Extract challenge information
        challenge_info = input_data.get('challenge_info', {})
        documents_info = input_data.get('documents', [])
        persona_info = input_data.get('persona', {})
        job_info = input_data.get('job_to_be_done', {})
        
        # Initialize persona analyzer
        persona_role = persona_info.get('role', 'Generic Analyst')
        job_task = job_info.get('task', 'Analyze documents for insights')
        
        persona_analyzer = PersonaAnalyzer(persona_role, job_task, str(self.output_folder))
        
        print(f"🎯 Challenge: {challenge_info.get('description', 'Document Analysis')}")
        print(f"👤 Persona: {persona_role}")
        print(f"📋 Task: {job_task}")
        print(f"📄 Documents: {len(documents_info)} files")
        print("=" * 50)
        
        # Process documents
        processed_documents = self.document_processor.process_all_documents()
        
        # Filter documents to match input list
        relevant_documents = self.filter_relevant_documents(processed_documents, documents_info)
        
        # Perform persona-driven analysis
        analysis_results = persona_analyzer.analyze_documents(relevant_documents)
        
        # Generate challenge-format output
        output_data = self.generate_challenge_output(
            challenge_info, documents_info, persona_info, job_info, 
            relevant_documents, analysis_results
        )
        
        # Save output
        self.save_challenge_output(output_data, challenge_info.get('challenge_id', 'unknown'))
        
        return output_data
    
    def filter_relevant_documents(self, processed_docs: List[Dict], document_info: List[Dict]) -> List[Dict]:
        """Filter processed documents to match the input document list."""
        relevant_docs = []
        input_filenames = {doc['filename'] for doc in document_info}
        
        for doc in processed_docs:
            filename = doc.get('metadata', {}).get('filename', '')
            if filename in input_filenames:
                relevant_docs.append(doc)
        
        return relevant_docs
    
    def generate_challenge_output(self, challenge_info: Dict, documents_info: List[Dict], 
                                persona_info: Dict, job_info: Dict, 
                                processed_docs: List[Dict], analysis_results: Dict) -> Dict[str, Any]:
        """Generate output in the expected challenge format."""
        
        # Create metadata section
        metadata = {
            "input_documents": [doc['filename'] for doc in documents_info],
            "persona": persona_info.get('role', 'Unknown'),
            "job_to_be_done": job_info.get('task', 'Unknown'),
            "processing_timestamp": datetime.now().isoformat()
        }
        
        # Extract key sections based on persona analysis
        extracted_sections = self.extract_key_sections(processed_docs, analysis_results)
        
        # Generate subsection analysis with refined text
        subsection_analysis = self.generate_subsection_analysis(processed_docs, analysis_results)
        
        # Construct final output
        output_data = {
            "metadata": metadata,
            "extracted_sections": extracted_sections,
            "subsection_analysis": subsection_analysis
        }
        
        return output_data
    
    def extract_key_sections(self, processed_docs: List[Dict], analysis_results: Dict) -> List[Dict]:
        """Extract key sections ranked by importance for the persona."""
        key_sections = []
        
        # Get document analyses
        document_analyses = analysis_results.get('document_analyses', [])
        
        # Create a mapping of filename to analysis
        analysis_map = {analysis['filename']: analysis for analysis in document_analyses}
        
        section_candidates = []
        
        # Collect all relevant sections from all documents
        for doc in processed_docs:
            filename = doc.get('metadata', {}).get('filename', '')
            sections = doc.get('sections', [])
            doc_analysis = analysis_map.get(filename, {})
            relevant_sections = doc_analysis.get('relevant_sections', [])
            
            # Add sections with relevance scores
            for section in relevant_sections:
                section_candidates.append({
                    'document': filename,
                    'section_title': section.get('title', 'Untitled Section'),
                    'relevance_score': section.get('relevance_score', 0),
                    'page_number': self.estimate_page_number(section),
                    'content': section.get('content', '')
                })
        
        # Sort by relevance score and take top sections
        section_candidates.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Format as expected output (top 5 sections)
        for i, section in enumerate(section_candidates[:5]):
            key_sections.append({
                "document": section['document'],
                "section_title": section['section_title'],
                "importance_rank": i + 1,
                "page_number": section['page_number']
            })
        
        return key_sections
    
    def generate_subsection_analysis(self, processed_docs: List[Dict], analysis_results: Dict) -> List[Dict]:
        """Generate detailed subsection analysis with refined text."""
        subsection_analysis = []
        
        # Get persona-specific extracts
        persona_extracts = analysis_results.get('persona_specific_extracts', {})
        document_analyses = analysis_results.get('document_analyses', [])
        
        # Create analysis map
        analysis_map = {analysis['filename']: analysis for analysis in document_analyses}
        
        # Process each document for subsection analysis
        for doc in processed_docs:
            filename = doc.get('metadata', {}).get('filename', '')
            doc_analysis = analysis_map.get(filename, {})
            key_extracts = doc_analysis.get('key_extracts', [])
            
            # Get the most relevant sections for detailed analysis
            relevant_sections = doc_analysis.get('relevant_sections', [])[:3]  # Top 3 sections per doc
            
            for section in relevant_sections:
                refined_text = self.create_refined_text(section, key_extracts)
                if refined_text:  # Only add if we have meaningful content
                    subsection_analysis.append({
                        "document": filename,
                        "refined_text": refined_text,
                        "page_number": self.estimate_page_number(section)
                    })
        
        return subsection_analysis
    
    def create_refined_text(self, section: Dict, key_extracts: List[str]) -> str:
        """Create refined, persona-relevant text from section content."""
        section_content = section.get('content', '')
        section_title = section.get('title', '')
        
        # If section content is too short, try to enhance with key extracts
        if len(section_content) < 100:
            # Find relevant extracts that might belong to this section
            relevant_extracts = []
            title_keywords = section_title.lower().split()
            
            for extract in key_extracts:
                extract_lower = extract.lower()
                if any(keyword in extract_lower for keyword in title_keywords if len(keyword) > 3):
                    relevant_extracts.append(extract)
            
            if relevant_extracts:
                section_content = ' '.join(relevant_extracts[:3])
        
        # Clean and refine the text
        refined_text = self.clean_and_structure_text(section_content, section_title)
        
        return refined_text
    
    def clean_and_structure_text(self, content: str, title: str) -> str:
        """Clean and structure text for better readability."""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = ' '.join(content.split())
        
        # If content is too long, truncate intelligently
        if len(content) > 800:
            sentences = content.split('. ')
            truncated_sentences = []
            char_count = 0
            
            for sentence in sentences:
                if char_count + len(sentence) < 750:
                    truncated_sentences.append(sentence)
                    char_count += len(sentence)
                else:
                    break
            
            content = '. '.join(truncated_sentences)
            if not content.endswith('.'):
                content += '.'
        
        return content
    
    def estimate_page_number(self, section: Dict) -> int:
        """Estimate page number for a section (placeholder logic)."""
        # In a real implementation, this would track actual page numbers
        # For now, we'll use a simple heuristic
        start_line = section.get('start_line', 0)
        estimated_page = max(1, (start_line // 50) + 1)  # Assume ~50 lines per page
        return min(estimated_page, 20)  # Cap at reasonable page number
    
    def save_challenge_output(self, output_data: Dict[str, Any], challenge_id: str):
        """Save the challenge output to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"challenge_output_{challenge_id}_{timestamp}.json"
        output_path = self.output_folder / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ Challenge output saved to: {output_path}")
        
        # Also save a readable summary
        self.save_readable_summary(output_data, challenge_id, timestamp)
    
    def save_readable_summary(self, output_data: Dict, challenge_id: str, timestamp: str):
        """Save a human-readable summary of the results."""
        summary_filename = f"challenge_summary_{challenge_id}_{timestamp}.txt"
        summary_path = self.output_folder / summary_filename
        
        metadata = output_data.get('metadata', {})
        sections = output_data.get('extracted_sections', [])
        subsections = output_data.get('subsection_analysis', [])
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("PERSONA-DRIVEN DOCUMENT INTELLIGENCE RESULTS\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("METADATA:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Persona: {metadata.get('persona', 'Unknown')}\n")
            f.write(f"Task: {metadata.get('job_to_be_done', 'Unknown')}\n")
            f.write(f"Documents: {len(metadata.get('input_documents', []))}\n")
            f.write(f"Processing Time: {metadata.get('processing_timestamp', 'Unknown')}\n\n")
            
            f.write("KEY EXTRACTED SECTIONS:\n")
            f.write("-" * 30 + "\n")
            for section in sections:
                f.write(f"{section.get('importance_rank', 0)}. {section.get('section_title', 'Untitled')}\n")
                f.write(f"   Document: {section.get('document', 'Unknown')}\n")
                f.write(f"   Page: {section.get('page_number', 'Unknown')}\n\n")
            
            f.write("DETAILED SUBSECTION ANALYSIS:\n")
            f.write("-" * 35 + "\n")
            for i, subsection in enumerate(subsections, 1):
                f.write(f"{i}. Document: {subsection.get('document', 'Unknown')}\n")
                f.write(f"   Page: {subsection.get('page_number', 'Unknown')}\n")
                f.write(f"   Content Preview: {subsection.get('refined_text', '')[:200]}...\n\n")
        
        print(f"📄 Readable summary saved to: {summary_path}")

def main():
    """Main function to run the persona-driven document intelligence system."""
    system = PersonaDocumentIntelligenceSystem()
    
    # Example of how to use with challenge input format
    sample_input = {
        "challenge_info": {
            "challenge_id": "round_1b_002",
            "test_case_name": "travel_planner",
            "description": "France Travel"
        },
        "documents": [
            {"filename": "South of France - Cities.pdf", "title": "South of France - Cities"},
            {"filename": "South of France - Cuisine.pdf", "title": "South of France - Cuisine"},
            {"filename": "South of France - History.pdf", "title": "South of France - History"},
            {"filename": "South of France - Restaurants and Hotels.pdf", "title": "South of France - Restaurants and Hotels"},
            {"filename": "South of France - Things to Do.pdf", "title": "South of France - Things to Do"},
            {"filename": "South of France - Tips and Tricks.pdf", "title": "South of France - Tips and Tricks"},
            {"filename": "South of France - Traditions and Culture.pdf", "title": "South of France - Traditions and Culture"}
        ],
        "persona": {
            "role": "Travel Planner"
        },
        "job_to_be_done": {
            "task": "Plan a trip of 4 days for a group of 10 college friends."
        }
    }
def extract_key_sections(self, processed_docs: List[Dict], analysis_results: Dict) -> List[Dict]:
    """Extract key sections ranked by importance for the persona."""
    extracted_sections = []
    
    # Get document analyses from persona analyzer results
    doc_analyses = analysis_results.get('document_analyses', [])
    
    for idx, doc_analysis in enumerate(doc_analyses, 1):
        filename = doc_analysis.get('filename', 'Unknown')
        relevance_score = doc_analysis.get('relevance_score', 0.0)
        key_extracts = doc_analysis.get('key_extracts', [])
        
        # Create section title based on first key extract or filename
        if key_extracts:
            section_title = key_extracts[0][:50] + "..." if len(key_extracts[0]) > 50 else key_extracts[0]
        else:
            # Fallback: create title from filename
            section_title = filename.replace('.pdf', '').replace('-', ' ').title()
        
        # Find the document to get page info
        page_number = 1  # Default
        for doc in processed_docs:
            if doc.get('metadata', {}).get('filename') == filename:
                # Try to extract page from first content or default to 1
                raw_content = doc.get('raw_content', '')
                if '--- Page' in raw_content:
                    try:
                        page_start = raw_content.find('--- Page') + 9
                        page_end = raw_content.find('---', page_start)
                        page_number = int(raw_content[page_start:page_end].strip())
                    except:
                        page_number = 1
                break
        
        extracted_sections.append({
            "document": filename,
            "section_title": section_title,
            "importance_rank": idx,  # Based on relevance order
            "page_number": page_number
        })
    
    # Sort by relevance score (higher scores first)
    extracted_sections.sort(key=lambda x: doc_analyses[x['importance_rank']-1].get('relevance_score', 0), reverse=True)
    
    # Re-assign ranks after sorting
    for idx, section in enumerate(extracted_sections, 1):
        section['importance_rank'] = idx
    
    return extracted_sections[:5]  # Return top 5 sections

def generate_subsection_analysis(self, processed_docs: List[Dict], analysis_results: Dict) -> List[Dict]:
    """Generate detailed subsection analysis with refined text."""
    subsection_analysis = []
    
    # Get persona-specific extracts
    persona_extracts = analysis_results.get('persona_specific_extracts', [])
    doc_analyses = analysis_results.get('document_analyses', [])
    
    for doc_analysis in doc_analyses:
        filename = doc_analysis.get('filename', 'Unknown')
        key_extracts = doc_analysis.get('key_extracts', [])
        
        # Find the corresponding processed document
        doc_content = ""
        for doc in processed_docs:
            if doc.get('metadata', {}).get('filename') == filename:
                doc_content = doc.get('raw_content', doc.get('content', ''))
                break
        
        # Extract refined text from key extracts
        for extract in key_extracts[:2]:  # Limit to first 2 extracts per document
            # Find page number for this extract
            page_number = 1
            if '--- Page' in doc_content and extract in doc_content:
                extract_pos = doc_content.find(extract)
                page_section = doc_content[:extract_pos]
                page_matches = page_section.count('--- Page')
                page_number = max(1, page_matches)
            
            # Clean and refine the text
            refined_text = self.refine_text_for_persona(extract, analysis_results.get('persona', ''))
            
            subsection_analysis.append({
                "document": filename,
                "refined_text": refined_text,
                "page_number": page_number
            })
    
    return subsection_analysis

def refine_text_for_persona(self, text: str, persona: str) -> str:
    """Refine text content to be more relevant for the specific persona."""
    # Clean up text
    refined = text.strip()
    
    # Remove extra whitespace and clean formatting
    refined = ' '.join(refined.split())
    
    # Truncate if too long (keep it manageable)
    if len(refined) > 500:
        refined = refined[:500] + "..."
    
    return refined

def save_challenge_output(self, output_data: Dict[str, Any], challenge_id: str):
    """Save the challenge output to files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save JSON output
    json_filename = f"challenge_output_{challenge_id}_{timestamp}.json"
    json_path = self.output_folder / json_filename
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    # Save readable summary
    summary_filename = f"challenge_summary_{challenge_id}_{timestamp}.txt"
    summary_path = self.output_folder / summary_filename
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("PERSONA-DRIVEN DOCUMENT INTELLIGENCE RESULTS\n")
        f.write("=" * 60 + "\n")
        f.write(f"Challenge ID: {challenge_id}\n")
        f.write(f"Persona: {output_data['metadata']['persona']}\n")
        f.write(f"Task: {output_data['metadata']['job_to_be_done']}\n")
        f.write(f"Documents: {len(output_data['metadata']['input_documents'])}\n")
        f.write(f"Processing Time: {output_data['metadata']['processing_timestamp']}\n\n")
        
        f.write("KEY EXTRACTED SECTIONS:\n")
        f.write("-" * 30 + "\n")
        for section in output_data['extracted_sections']:
            f.write(f"Rank {section['importance_rank']}: {section['section_title']}\n")
            f.write(f"Document: {section['document']} (Page {section['page_number']})\n\n")
        
        f.write("DETAILED SUBSECTION ANALYSIS:\n")
        f.write("-" * 35 + "\n")
        for analysis in output_data['subsection_analysis']:
            f.write(f"Document: {analysis['document']} (Page {analysis['page_number']})\n")
            f.write(f"Content: {analysis['refined_text'][:200]}...\n\n")
    
    print(f"✅ Challenge output saved to: {json_path}")
    print(f"📄 Readable summary saved to: {summary_path}")
    
    # Process the input
    results = system.process_challenge_input(sample_input)
    
    return results

if __name__ == "__main__":
    main()