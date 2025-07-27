\# Persona-Driven Document Intelligence



A sophisticated Python-based system that analyzes multiple PDF documents through the lens of specific personas to extract targeted insights and generate actionable intelligence.



\## 🎯 Overview



This system transforms how we analyze documents by applying persona-specific analysis to extract relevant information based on different professional perspectives. Whether you're a travel planner, nutritionist, business analyst, or any other professional role, this tool adapts its analysis to your specific needs.



\## ✨ Features



\- \*\*Multi-Document Processing\*\*: Analyze multiple PDF files simultaneously

\- \*\*Persona-Driven Analysis\*\*: Extract insights based on specific professional perspectives

\- \*\*Intelligent Ranking\*\*: Prioritize information based on relevance to your persona and task

\- \*\*Structured Output\*\*: Generate both JSON data and human-readable summaries

\- \*\*Challenge Mode\*\*: Pre-configured scenarios for quick deployment

\- \*\*Flexible Configuration\*\*: Easy-to-use JSON input files for custom analysis



\## 🚀 Quick Start



\### Prerequisites



\- Python 3.8+

\- Virtual environment (recommended)



\### Installation



1\. \*\*Clone the repository:\*\*

&nbsp;  ```bash

&nbsp;  git clone https://github.com/yourusername/persona-document-intelligence.git

&nbsp;  cd persona-document-intelligence

&nbsp;  ```



2\. \*\*Create and activate virtual environment:\*\*

&nbsp;  ```bash

&nbsp;  python -m venv venv

&nbsp;  # Windows

&nbsp;  venv\\Scripts\\activate

&nbsp;  # macOS/Linux

&nbsp;  source venv/bin/activate

&nbsp;  ```



3\. \*\*Install dependencies:\*\*

&nbsp;  ```bash

&nbsp;  pip install -r requirements.txt

&nbsp;  ```



\### Basic Usage



1\. \*\*Place your PDF files in the input directory:\*\*

&nbsp;  ```bash

&nbsp;  mkdir data/input

&nbsp;  # Copy your PDF files to data/input/

&nbsp;  ```



2\. \*\*Create or modify an input configuration:\*\*

&nbsp;  ```json

&nbsp;  {

&nbsp;    "challenge\_id": "your\_analysis\_name",

&nbsp;    "persona": "Travel Planner",

&nbsp;    "task": "Plan a 4-day trip for college friends",

&nbsp;    "document\_folder": "data/input"

&nbsp;  }

&nbsp;  ```



3\. \*\*Run the analysis:\*\*

&nbsp;  ```bash

&nbsp;  python run\_analysis.py your\_config.json

&nbsp;  ```



\## 📋 Example Use Cases



\### Travel Planning

\- \*\*Persona\*\*: Travel Planner

\- \*\*Task\*\*: Create comprehensive itineraries

\- \*\*Documents\*\*: City guides, restaurant lists, attraction information



\### Meal Planning

\- \*\*Persona\*\*: Nutritionist

\- \*\*Task\*\*: Design balanced weekly menus

\- \*\*Documents\*\*: Recipe collections, dietary guidelines, ingredient lists



\### Business Analysis

\- \*\*Persona\*\*: Business Analyst

\- \*\*Task\*\*: Market research and competitive analysis

\- \*\*Documents\*\*: Industry reports, company profiles, market data



\## 🏗️ Project Structure



```

persona-document-intelligence/

├── src/

│   ├── document\_processor.py    # PDF processing and text extraction

│   ├── persona\_analyzer.py      # Persona-specific analysis engine

│   ├── ranking\_engine.py        # Content relevance ranking

│   ├── section\_extractor.py     # Document section processing

│   └── main.py                  # Core orchestration logic

├── data/

│   ├── input/                   # Input PDF files

│   └── output/                  # Generated analysis results

├── run\_analysis.py              # Main execution script

├── sample\_challenge\_input.json  # Example configuration

└── requirements.txt             # Python dependencies

```



\## ⚙️ Configuration



\### Input JSON Format



```json

{

&nbsp; "challenge\_id": "unique\_identifier",

&nbsp; "persona": "Professional Role (e.g., Travel Planner, Nutritionist)",

&nbsp; "task": "Specific objective for the analysis",

&nbsp; "document\_folder": "path/to/pdf/files"

}

```



\### Available Personas



\- \*\*Travel Planner\*\*: Tourism, itinerary planning, destination analysis

\- \*\*Nutritionist\*\*: Dietary analysis, meal planning, health optimization

\- \*\*Business Analyst\*\*: Market research, competitive analysis, strategy

\- \*\*Meal Planner\*\*: Recipe organization, menu creation, cooking workflows

\- \*\*Event Coordinator\*\*: Venue analysis, logistics planning, scheduling

\- \*\*Research Analyst\*\*: Data synthesis, trend analysis, insights generation



\## 📊 Output



The system generates multiple output formats:



1\. \*\*Structured JSON\*\*: Machine-readable analysis results

2\. \*\*Human-readable Summary\*\*: Formatted text with key insights

3\. \*\*Challenge Output\*\*: Persona-specific recommendations and action items



\### Example Output Structure



```json

{

&nbsp; "challenge\_id": "dinner\_planning",

&nbsp; "persona": "Meal Planner",

&nbsp; "analysis\_results": {

&nbsp;   "document\_insights": \[...],

&nbsp;   "persona\_recommendations": \[...],

&nbsp;   "ranked\_sections": \[...]

&nbsp; },

&nbsp; "generated\_summary": "Human-readable insights..."

}

```



\## 🛠️ Advanced Usage



\### Custom Persona Creation



You can extend the system with custom personas by modifying the persona analysis logic in `src/persona\_analyzer.py`.



\### Batch Processing



Process multiple configurations:



```bash

\# Create multiple input files

python run\_analysis.py config1.json

python run\_analysis.py config2.json

python run\_analysis.py config3.json

```



\### Integration with Other Systems



The JSON output format makes it easy to integrate with:

\- Dashboard applications

\- Reporting systems

\- API endpoints

\- Database storage



\## 🔧 Development



\### Running Tests



```bash

\# Add your test commands here

python -m pytest tests/

```



\### Contributing



1\. Fork the repository

2\. Create a feature branch

3\. Make your changes

4\. Add tests if applicable

5\. Submit a pull request



\## 📝 Examples



\### Travel Planning Example



```bash

\# Input: South of France travel documents

\# Persona: Travel Planner

\# Task: 4-day itinerary for 10 college friends

python run\_analysis.py sample\_challenge\_input.json

```



\### Nutrition Analysis Example



```bash

\# Input: Dinner recipe collections

\# Persona: Nutritionist

\# Task: Weekly balanced meal planning

python run\_analysis.py nutrition\_challenge\_input.json

```



\## 🚨 Troubleshooting



\*\*Common Issues:\*\*



1\. \*\*JSON Format Error\*\*: Ensure your input JSON is properly formatted

2\. \*\*PDF Processing Error\*\*: Check that PDF files are not corrupted or password-protected

3\. \*\*Missing Dependencies\*\*: Run `pip install -r requirements.txt`



\## 📄 License



This project is licensed under the MIT License - see the LICENSE file for details.



\## 🤝 Contributing



Contributions are welcome! Please feel free to submit a Pull Request.



\## 📞 Support



If you encounter any issues or have questions, please open an issue on GitHub.



---



\*\*Built with ❤️ for intelligent document analysis\*\*

