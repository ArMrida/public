# RAG Expert - Java Maven Development Assistant

RAG Expert is an intelligent development assistant system that uses Retrieval-Augmented Generation (RAG) technology to support the development of complex Java Maven projects.

## Current Capabilities

The current version of the system supports the following features:

- **Document Management**
  - Automatic loading of Java source code and documentation from the `data` folder
  - Intelligent chunking of documents into semantic units
  - Vector representation creation using HuggingFace embedding model
  - Chromadb vector database management with persistent storage

- **Semantic Search**
  - Retrieval of relevant code snippets based on natural language questions
  - Context-sensitive search in development documentation
  - Automatic creation of missing collections during search

- **LLM Integration**
  - Using Claude Haiku model (claude-3-haiku-20240307)
  - Context-based response generation from retrieved documents
  - Intelligent interpretation of code snippets and documentation

- **Web User Interface**
  - Interactive chat interface for asking development questions
  - Database management functions (creation, deletion, update)
  - Document listing and display
  - Markdown formatting and code highlighting of responses

- **Robust Error Handling**
  - Detailed logging for tracking operations
  - Automatic error troubleshooting attempts
  - Automatic handling of permission issues
  - Graceful handling of error states in the user interface

## Folder Structure

The RAG Expert system has the following folder structure:

```
RAG-Expert/
├── app/
│   ├── database.py        # Document database manager
│   ├── __init__.py
│   ├── llm_service.py     # Claude API connection
│   ├── logs/              # Application logs 
│   ├── main.py            # Main application and web server
│   └── __pycache__/       # Python bytecode files
├── chroma_db/             # Vector database storage
├── data/
│   ├── docs/
│   │   └── project.MD     # Project documentation
│   └── readme.md          # Development project description
├── logs/                  # Central logs
├── readme.md              # Project description
├── requirements.txt       # Dependency list
├── static/
│   └── js/
│       └── app.js         # Frontend JavaScript
└── templates/
    └── index.html         # Web interface template
```

## Installation and Usage Guide

### Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Linux/MacOS)
source venv/bin/activate
# OR for Windows
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Required Dependencies

The system uses the following main dependencies:
```
langchain==0.1.0
langchain-anthropic==0.1.1
langchain-community==0.0.17
sentence-transformers==2.2.2
chromadb==0.6.3
flask==2.3.3
python-dotenv==1.0.0
anthropic==0.8.1
```

### Usage

```bash
# Set environment variables
export ANTHROPIC_API_KEY="your_api_key_here"

# Start the application
cd RAG-Expert
python app/main.py
```

The web interface is available at: http://localhost:8080

## Troubleshooting Guide

The system has robust error handling mechanisms. Below we summarize the most common problems and their solutions.

(The full troubleshooting guide can be found in the original README)

## Current Limitations and Future Development Goals

The system is currently **unable to** do the following, which are future development goals:

1. Automatic project documentation maintenance
2. Git version control automation
3. Maven build process integration
4. Automatic test result analysis
5. Autonomous development capability

## Development Plan Time Estimates

| Development Task | Estimated Time | With Claude AI |
|-----------------|----------------|----------------|
| Project.md automation | 2-3 days | 1 day |
| Git integration | 1-2 weeks | 3-5 days |
| Maven integration | 1 week | 2-3 days |
| Testing integration | 1-2 weeks | 3-5 days |
| Autonomous development | 2-3 weeks | 1-2 weeks |

## Development Best Practices

Best practices to follow during project development:

1. Error resistance everywhere
2. Detailed logging
3. Environment variables and configuration management
4. Unified Frontend-backend communication
5. Comprehensive testing

## License

MIT License

## Contributing

The project is open to contributions. Please follow the standard fork-and-pull-request workflow.

---

Developer: Máté Vitkovits
Last updated: February 20, 2025
