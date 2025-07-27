#!/usr/bin/env python3
"""
Updated run_analysis.py script for Persona-Driven Document Intelligence System
Now supports both interactive mode and challenge input format.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from main import PersonaDocumentIntelligenceSystem
    from document_processor import DocumentProcessor
    from persona_analyzer import PersonaAnalyzer
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Make sure all required modules are in the src/ directory")
    sys.exit(1)

def interactive_mode():
    """Run the system in interactive mode (original functionality)."""
    input_folder = Path("data/input")
    
    print("=== Persona-Driven Document Intelligence System ===")
    
    # 1. Document Collection
    print("1. DOCUMENT COLLECTION:")
    print("Place your PDF files in the 'data/input/' folder")
    
    if not input_folder.exists():
        print(f"❌ Input folder '{input_folder}' does not exist!")
        print("Please create the folder and add your PDF files.")
        return
    
    pdf_files = list(input_folder.glob("*.pdf"))
    if not pdf_files:
        print("❌ No PDF files found in the input folder!")
        print("Please add PDF files to analyze.")
        return
    
    print(f"Found {len(pdf_files)} PDF files:")
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf_file.name}")
    
    # 2. Persona Definition
    print("\n2. PERSONA DEFINITION:")
    print("Examples:")
    print("   - PhD Researcher in Computational Biology")
    print("   - Investment Analyst")
    print("   - Travel Content Writer")
    print("   - Marketing Manager")
    print("   - Software Engineer")
    
    persona = input("Enter your persona: ").strip()
    if not persona:
        persona = "Generic Analyst"
        print(f"Using default persona: {persona}")
    
    # 3. Job-to-be-done
    print("\n3. JOB-TO-BE-DONE:")
    print("Examples:")
    print("   - Prepare a comprehensive literature review focusing on methodologies")
    print("   - Analyze revenue trends and market positioning strategies")
    print("   - Create comprehensive travel guide covering attractions, cuisine, culture, and practical tips")
    print("   - Extract technical specifications for product development")
    
    job_to_be_done = input("Enter your job-to-be-done: ").strip()
    if not job_to_be_done:
        job_to_be_done = "Analyze documents for key insights"
        print(f"Using default job: {job_to_be_done}")
    
    # Process documents
    print("\n" + "="*50)
    print("PROCESSING...")
    print("="*50)
    print(f"📁 Documents: {len(pdf_files)} files")
    print(f"👤 Persona: {persona}")
    print(f"🎯 Job: {job_to_be_done}")
    
    try:
        # Initialize system
        system = PersonaDocumentIntelligenceSystem()
        
        # Create challenge-format input
        challenge_input = {
            "challenge_info": {
                "challenge_id": f"interactive_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "test_case_name": "interactive_analysis",
                "description": "Interactive Document Analysis"
            },
            "documents": [
                {"filename": pdf_file.name, "title": pdf_file.stem} 
                for pdf_file in pdf_files
            ],
            "persona": {
                "role": persona
            },
            "job_to_be_done": {
                "task": job_to_be_done
            }
        }
        
        # Process
        results = system.process_challenge_input(challenge_input)
        
        print("\n✅ PROCESSING COMPLETE!")
        print(f"📊 Analyzed {len(results.get('extracted_sections', []))} key sections")
        print(f"📝 Generated {len(results.get('subsection_analysis', []))} detailed analyses")
        print("\nCheck the 'data/output/' folder for detailed results.")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        print("Please check that all required dependencies are installed.")
        return

def challenge_mode(input_file: str):
    """Run the system in challenge mode with JSON input."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ Input file '{input_file}' does not exist!")
        return
    
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            challenge_input = json.load(f)
        
        print("=== Challenge Mode: Persona-Driven Document Intelligence ===")
        
        # Initialize and run system
        system = PersonaDocumentIntelligenceSystem()
        results = system.process_challenge_input(challenge_input)
        
        print("\n✅ CHALLENGE PROCESSING COMPLETE!")
        print(f"📊 Challenge ID: {challenge_input.get('challenge_info', {}).get('challenge_id', 'Unknown')}")
        print(f"📝 Results saved to data/output/ folder")
        
        return results
        
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON input: {e}")
        return
    except Exception as e:
        print(f"❌ Error during challenge processing: {e}")
        return

def main():
    """Main function with mode selection."""
    if len(sys.argv) > 1:
        # Command line argument provided - assume it's a JSON input file
        input_file = sys.argv[1]
        challenge_mode(input_file)
    else:
        # No arguments - run interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()