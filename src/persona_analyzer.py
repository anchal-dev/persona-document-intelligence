import json
import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from pathlib import Path

class PersonaAnalyzer:
    """
    Analyzes documents through the lens of a specific persona and job-to-be-done.
    Extracts relevant information and generates persona-specific insights.
    """
    
    def __init__(self, persona: str, job_to_be_done: str, output_folder: str = "data/output"):
        self.persona = persona
        self.job_to_be_done = job_to_be_done
        self.output_folder = Path(output_folder)
        self.output_folder.mkdir(parents=True, exist_ok=True)
        
        # Define persona-specific analysis patterns
        self.analysis_patterns = self.define_analysis_patterns()
    
    def define_analysis_patterns(self) -> Dict[str, Any]:
        """
        Define analysis patterns based on common persona types.
        This could be expanded with more sophisticated persona matching.
        """
        patterns = {
            'travel_content_writer': {
                'key_sections': ['attractions', 'cuisine', 'culture', 'hotels', 'restaurants', 'tips', 'history', 'traditions'],
                'extraction_keywords': ['visit', 'taste', 'experience', 'stay', 'eat', 'see', 'do', 'recommend', 'must', 'best', 'top'],
                'format_preferences': ['detailed descriptions', 'practical information', 'insider tips', 'cultural context'],
                'output_structure': ['overview', 'attractions', 'dining', 'culture', 'practical_tips']
            },
            'researcher': {
                'key_sections': ['methodology', 'results', 'conclusions', 'references', 'data', 'analysis'],
                'extraction_keywords': ['study', 'research', 'method', 'result', 'conclusion', 'data', 'analysis', 'finding'],
                'format_preferences': ['citations', 'methodologies', 'key findings', 'data points'],
                'output_structure': ['literature_review', 'methodologies', 'key_findings', 'references']
            },
            'analyst': {
                'key_sections': ['trends', 'metrics', 'performance', 'market', 'revenue', 'growth'],
                'extraction_keywords': ['trend', 'increase', 'decrease', 'percent', 'growth', 'market', 'revenue', 'profit'],
                'format_preferences': ['quantitative data', 'trends', 'comparisons', 'forecasts'],
                'output_structure': ['executive_summary', 'key_metrics', 'trends', 'recommendations']
            },
            'student': {
                'key_sections': ['concepts', 'definitions', 'examples', 'formulas', 'principles'],
                'extraction_keywords': ['define', 'concept', 'principle', 'formula', 'example', 'important', 'key'],
                'format_preferences': ['clear definitions', 'examples', 'step-by-step', 'summaries'],
                'output_structure': ['key_concepts', 'definitions', 'examples', 'study_notes']
            },
            'default': {
                'key_sections': ['overview', 'main_points', 'details', 'summary'],
                'extraction_keywords': ['important', 'key', 'main', 'significant', 'notable'],
                'format_preferences': ['organized information', 'clear structure', 'relevant details'],
                'output_structure': ['overview', 'main_points', 'details', 'summary']
            }
        }
        
        # Try to match persona to patterns
        persona_lower = self.persona.lower()
        for pattern_key in patterns.keys():
            if any(keyword in persona_lower for keyword in pattern_key.split('_')):
                return patterns[pattern_key]
        
        return patterns['default']
    
    def analyze_documents(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all documents from the persona's perspective.
        """
        print(f"Analyzing documents as: {self.persona}")
        print(f"Job to be done: {self.job_to_be_done}")
        print("=" * 50)
        
        analysis_results = {
            'persona': self.persona,
            'job_to_be_done': self.job_to_be_done,
            'analysis_timestamp': datetime.now().isoformat(),
            'document_analyses': [],
            'consolidated_insights': {},
            'persona_specific_extracts': {},
            'recommendations': []
        }
        
        # Analyze each document
        for doc in documents:
            doc_analysis = self.analyze_single_document(doc)
            analysis_results['document_analyses'].append(doc_analysis)
        
        # Generate consolidated insights
        analysis_results['consolidated_insights'] = self.generate_consolidated_insights(documents)
        
        # Extract persona-specific information
        analysis_results['persona_specific_extracts'] = self.extract_persona_specific_info(documents)
        
        # Generate recommendations
        analysis_results['recommendations'] = self.generate_recommendations(documents)
        
        # Save analysis results
        self.save_analysis_results(analysis_results)
        
        return analysis_results
    
    def analyze_single_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single document from the persona's perspective."""
        filename = document.get('metadata', {}).get('filename', 'Unknown')
        content = document.get('content', '')
        sections = document.get('sections', [])
        
        print(f"Analyzing: {filename}")
        
        doc_analysis = {
            'filename': filename,
            'relevance_score': self.calculate_relevance_score(content),
            'key_extracts': self.extract_key_information(content),
            'relevant_sections': self.identify_relevant_sections(sections),
            'persona_insights': self.generate_persona_insights(content),
            'actionable_items': self.extract_actionable_items(content)
        }
        
        return doc_analysis
    
    def calculate_relevance_score(self, content: str) -> float:
        """Calculate how relevant the document is to the persona and job."""
        content_lower = content.lower()
        job_lower = self.job_to_be_done.lower()
        
        # Count matches with job keywords
        job_keywords = re.findall(r'\b\w+\b', job_lower)
        job_matches = sum(1 for keyword in job_keywords if keyword in content_lower)
        
        # Count matches with persona-specific keywords
        persona_keywords = self.analysis_patterns['extraction_keywords']
        persona_matches = sum(1 for keyword in persona_keywords if keyword in content_lower)
        
        # Calculate relevance score (0-1)
        total_possible = len(job_keywords) + len(persona_keywords)
        total_matches = job_matches + persona_matches
        
        relevance_score = min(total_matches / total_possible, 1.0) if total_possible > 0 else 0.0
        
        return round(relevance_score, 3)
    
    def extract_key_information(self, content: str) -> List[str]:
        """Extract key information based on persona needs."""
        key_extracts = []
        sentences = re.split(r'[.!?]+', content)
        
        keywords = self.analysis_patterns['extraction_keywords']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Skip very short sentences
                # Check if sentence contains relevant keywords
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in keywords):
                    key_extracts.append(sentence)
        
        # Return top extracts (limit to avoid overwhelming output)
        return key_extracts[:10]
    
    def identify_relevant_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify sections most relevant to the persona."""
        relevant_sections = []
        key_section_keywords = self.analysis_patterns['key_sections']
        
        for section in sections:
            title = section.get('title', '').lower()
            content = section.get('content', '').lower()
            
            # Check if section is relevant
            relevance_score = 0
            for keyword in key_section_keywords:
                if keyword in title or keyword in content:
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_section = section.copy()
                relevant_section['relevance_score'] = relevance_score
                relevant_sections.append(relevant_section)
        
        # Sort by relevance
        relevant_sections.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_sections[:5]  # Return top 5 most relevant sections
    
    def generate_persona_insights(self, content: str) -> List[str]:
        """Generate insights specific to the persona's perspective."""
        insights = []
        content_lower = content.lower()
        
        # Travel Content Writer specific insights
        if 'travel' in self.persona.lower() or 'writer' in self.persona.lower():
            if 'restaurant' in content_lower or 'food' in content_lower:
                insights.append("Rich culinary content available for food section")
            if 'history' in content_lower or 'culture' in content_lower:
                insights.append("Cultural and historical context for authentic storytelling")
            if 'tip' in content_lower or 'recommend' in content_lower:
                insights.append("Practical travel tips and recommendations identified")
        
        # Researcher specific insights
        elif 'research' in self.persona.lower() or 'phd' in self.persona.lower():
            if 'method' in content_lower or 'study' in content_lower:
                insights.append("Methodological information available")
            if 'data' in content_lower or 'result' in content_lower:
                insights.append("Data and results section identified")
        
        # Analyst specific insights
        elif 'analyst' in self.persona.lower():
            if any(word in content_lower for word in ['trend', 'growth', 'market', 'revenue']):
                insights.append("Market and trend information available")
            if any(word in content_lower for word in ['percent', '%', 'increase', 'decrease']):
                insights.append("Quantitative data points identified")
        
        # Generic insights if no specific persona match
        if not insights:
            insights.append("Content contains relevant information for specified job")
        
        return insights
    
    def extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items based on the job-to-be-done."""
        actionable_items = []
        sentences = re.split(r'[.!?]+', content)
        
        # Look for imperative sentences or recommendations
        action_patterns = [
            r'\b(should|must|need to|recommended|suggest|advise)\b.*',
            r'\b(visit|try|taste|see|do|avoid|bring|book)\b.*',
            r'\b(tip|advice|recommendation|warning)\b.*'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 15:
                for pattern in action_patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        actionable_items.append(sentence)
                        break
        
        return actionable_items[:8]  # Limit to top actionable items
    
    def generate_consolidated_insights(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate insights across all documents."""
        all_content = " ".join([doc.get('content', '') for doc in documents])
        
        consolidated = {
            'total_documents_analyzed': len(documents),
            'overall_relevance': self.calculate_relevance_score(all_content),
            'key_themes': self.extract_key_themes(documents),
            'content_gaps': self.identify_content_gaps(documents),
            'cross_document_patterns': self.find_cross_document_patterns(documents)
        }
        
        return consolidated
    
    def extract_key_themes(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Extract recurring themes across documents."""
        all_sections = []
        for doc in documents:
            sections = doc.get('sections', [])
            all_sections.extend([s.get('title', '').lower() for s in sections])
        
        # Count theme frequency
        theme_counts = {}
        for section_title in all_sections:
            words = re.findall(r'\b\w+\b', section_title)
            for word in words:
                if len(word) > 3:
                    theme_counts[word] = theme_counts.get(word, 0) + 1
        
        # Get top themes
        top_themes = sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return [theme for theme, count in top_themes if count > 1]
    
    def identify_content_gaps(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Identify potential gaps in content for the job-to-be-done."""
        gaps = []
        job_lower = self.job_to_be_done.lower()
        all_content = " ".join([doc.get('content', '') for doc in documents]).lower()
        
        # Check for common travel guide elements if it's a travel-related job
        if 'travel' in job_lower or 'guide' in job_lower:
            travel_elements = ['transportation', 'budget', 'weather', 'language', 'currency', 'safety']
            for element in travel_elements:
                if element not in all_content:
                    gaps.append(f"Missing {element} information")
        
        # Check for job-specific requirements
        job_keywords = re.findall(r'\b\w+\b', job_lower)
        for keyword in job_keywords:
            if keyword not in all_content and len(keyword) > 3:
                gaps.append(f"Limited coverage of {keyword}")
        
        return gaps[:5]  # Limit to top gaps
    
    def find_cross_document_patterns(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Find patterns that appear across multiple documents."""
        patterns = []
        
        # Look for repeated phrases or concepts
        all_contents = [doc.get('content', '') for doc in documents]
        
        # Simple pattern: check for phrases that appear in multiple documents
        common_phrases = {}
        for content in all_contents:
            # Extract phrases of 2-4 words
            words = re.findall(r'\b\w+\b', content.lower())
            for i in range(len(words) - 1):
                phrase = ' '.join(words[i:i+2])
                if len(phrase) > 6:  # Skip very short phrases
                    common_phrases[phrase] = common_phrases.get(phrase, 0) + 1
        
        # Find phrases that appear in multiple documents
        cross_doc_phrases = [(phrase, count) for phrase, count in common_phrases.items() if count >= min(2, len(documents))]
        cross_doc_phrases.sort(key=lambda x: x[1], reverse=True)
        
        patterns = [f"'{phrase}' appears across multiple documents" for phrase, count in cross_doc_phrases[:5]]
        
        return patterns
    
    def extract_persona_specific_info(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract information specifically organized for the persona."""
        structure = self.analysis_patterns['output_structure']
        persona_extracts = {}
        
        for category in structure:
            persona_extracts[category] = []
        
        # Extract information into persona-specific categories
        for doc in documents:
            content = doc.get('content', '')
            sections = doc.get('sections', [])
            
            # Categorize content based on persona needs
            for section in sections:
                title = section.get('title', '').lower()
                section_content = section.get('content', '')
                
                # Map sections to persona categories
                for category in structure:
                    if self.matches_category(title, section_content, category):
                        persona_extracts[category].append({
                            'source': doc.get('metadata', {}).get('filename', 'Unknown'),
                            'title': section.get('title', ''),
                            'content': section_content[:500] + "..." if len(section_content) > 500 else section_content
                        })
        
        return persona_extracts
    
    def matches_category(self, title: str, content: str, category: str) -> bool:
        """Check if content matches a persona-specific category."""
        text = (title + " " + content).lower()
        
        category_keywords = {
            'overview': ['overview', 'introduction', 'about', 'general'],
            'attractions': ['attraction', 'visit', 'see', 'place', 'site', 'landmark'],
            'dining': ['restaurant', 'food', 'eat', 'cuisine', 'dining', 'taste'],
            'culture': ['culture', 'tradition', 'history', 'local', 'heritage'],
            'practical_tips': ['tip', 'advice', 'recommend', 'should', 'how to'],
            'main_points': ['important', 'key', 'main', 'primary'],
            'details': ['detail', 'specific', 'information', 'data'],
            'summary': ['summary', 'conclusion', 'overview', 'recap']
        }
        
        keywords = category_keywords.get(category, [category])
        return any(keyword in text for keyword in keywords)
    
    def generate_recommendations(self, documents: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on the analysis."""
        recommendations = []
        
        # Analyze document collection completeness
        total_docs = len(documents)
        total_content = sum(doc.get('word_count', 0) for doc in documents)
        
        if total_docs < 5:
            recommendations.append("Consider adding more source documents for comprehensive coverage")
        
        if total_content < 10000:
            recommendations.append("Content volume may be insufficient for comprehensive guide")
        
        # Job-specific recommendations
        job_lower = self.job_to_be_done.lower()
        if 'guide' in job_lower:
            recommendations.append("Organize content into clear sections with practical information")
            recommendations.append("Include actionable tips and recommendations throughout")
        
        if 'comprehensive' in job_lower:
            recommendations.append("Ensure all major topics are covered with sufficient detail")
            recommendations.append("Cross-reference information across documents for consistency")
        
        # Persona-specific recommendations
        if 'writer' in self.persona.lower():
            recommendations.append("Focus on engaging narrative and descriptive content")
            recommendations.append("Include personal insights and authentic experiences")
        
        return recommendations
    
    def save_analysis_results(self, analysis_results: Dict[str, Any]):
        """Save analysis results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_folder / f"persona_analysis_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
        
        print(f"Analysis results saved to: {output_file}")
        
        # Also create a readable summary
        self.create_readable_summary(analysis_results, timestamp)
    
    def create_readable_summary(self, analysis_results: Dict[str, Any], timestamp: str):
        """Create a human-readable summary of the analysis."""
        summary_file = self.output_folder / f"analysis_summary_{timestamp}.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("PERSONA-DRIVEN DOCUMENT ANALYSIS SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Persona: {analysis_results['persona']}\n")
            f.write(f"Job to be Done: {analysis_results['job_to_be_done']}\n")
            f.write(f"Analysis Date: {analysis_results['analysis_timestamp']}\n\n")
            
            f.write("CONSOLIDATED INSIGHTS:\n")
            f.write("-" * 30 + "\n")
            insights = analysis_results.get('consolidated_insights', {})
            f.write(f"Documents Analyzed: {insights.get('total_documents_analyzed', 0)}\n")
            f.write(f"Overall Relevance Score: {insights.get('overall_relevance', 0):.3f}\n")
            f.write(f"Key Themes: {', '.join(insights.get('key_themes', []))}\n\n")
            
            f.write("DOCUMENT ANALYSIS:\n")
            f.write("-" * 20 + "\n")
            for doc_analysis in analysis_results.get('document_analyses', []):
                f.write(f"• {doc_analysis.get('filename', 'Unknown')}\n")
                f.write(f"  Relevance Score: {doc_analysis.get('relevance_score', 0):.3f}\n")
                f.write(f"  Key Insights: {len(doc_analysis.get('persona_insights', []))}\n")
                f.write(f"  Actionable Items: {len(doc_analysis.get('actionable_items', []))}\n\n")
            
            f.write("RECOMMENDATIONS:\n")
            f.write("-" * 20 + "\n")
            for rec in analysis_results.get('recommendations', []):
                f.write(f"• {rec}\n")
        
        print(f"Readable summary saved to: {summary_file}")