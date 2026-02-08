# Legal Document Navigator

An intelligent legal document search and question-answering system using Retrieval-Augmented Generation (RAG). This application allows legal professionals to upload documents and query them using natural language.

![Legal Document Navigator](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green)

## Features

- 📄 **Document Upload**: Support for PDF, DOCX, and TXT files
- 🔍 **Semantic Search**: Find relevant information using natural language queries
- 🤖 **AI-Powered Answers**: LLM-generated responses grounded in your documents
- 📊 **Source Citations**: Track which documents and pages were used
- 🎨 **Modern UI**: Clean, professional interface with drag-and-drop upload
- ⚡ **Fast & Efficient**: ChromaDB vector store for quick retrieval
- 🔒 **Local Processing**: Documents processed and stored locally

## Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **LangChain**: Framework for LLM applications
- **ChromaDB**: Vector database for embeddings
- **Sentence Transformers**: Text embedding models
- **NVIDIA API**: LLM inference (Llama 3.1)

### Frontend
- **Vanilla JavaScript**: No framework dependencies
- **Modern CSS**: Responsive design with CSS Grid/Flexbox
- **HTML5**: Semantic markup

## Architecture

```
User Query → Embedding → Vector Search → Context Retrieval → LLM Generation → Response
     ↑                                                                            ↓
     └─────────────────────── Document Upload ──────────────────────────────────┘
                                     ↓
                           Chunking → Embedding → Storage
```

## Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- NVIDIA API key (free tier available)

### Step 1: Clone or Download

```bash
cd legal-document-navigator
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your NVIDIA API key:

```env
NVIDIA_API_KEY=your_api_key_here
```

**Get a free NVIDIA API key:**
1. Visit https://build.nvidia.com/
2. Sign up for a free account
3. Navigate to API Catalog
4. Select a model (e.g., Llama 3.1)
5. Click "Get API Key"

### Step 5: Run the Application

```bash
python main.py
```

The application will start at `http://localhost:8000`

## Usage

### 1. Upload Documents

- Click the upload area or drag & drop files
- Supported formats: PDF, DOCX, TXT
- Maximum file size: 50MB
- Documents are automatically processed and indexed

### 2. Query Your Documents

Use natural language queries like:
- "Find all clauses about termination in the last 10 contracts"
- "What are the liability limitations?"
- "Summarize the payment terms"
- "Which documents mention intellectual property rights?"

### 3. Review Results

- Get AI-generated answers grounded in your documents
- See source citations with file names and page numbers
- View confidence scores for each response

## API Endpoints

### Health Check
```http
GET /api/health
```

### Upload Document
```http
POST /api/upload
Content-Type: multipart/form-data

file: <document file>
```

### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "query": "Find termination clauses",
  "top_k": 5,
  "include_sources": true
}
```

### Search Documents
```http
POST /api/search
Content-Type: application/json

{
  "query": "contract terms",
  "top_k": 10
}
```

### Get Statistics
```http
GET /api/stats
```

### Clear All Documents
```http
DELETE /api/documents
```

## Configuration

Edit `config.py` to customize:

```python
# Document processing
CHUNK_SIZE = 1000          # Size of text chunks
CHUNK_OVERLAP = 200        # Overlap between chunks
MAX_FILE_SIZE_MB = 50      # Maximum upload size

# Retrieval
TOP_K_RESULTS = 5          # Number of documents to retrieve
SIMILARITY_THRESHOLD = 0.7 # Minimum similarity score

# Models
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "meta/llama-3.1-70B-instruct"
```

## Project Structure

```
legal-document-navigator/
├── main.py                    # FastAPI entry point
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── models/
│   ├── document_processor.py # Document loading & chunking
│   ├── embeddings.py         # Embedding generation
│   └── llm_handler.py        # LLM integration
├── services/
│   ├── vector_store.py       # ChromaDB management
│   └── query_service.py      # RAG orchestration
├── api/
│   ├── routes.py             # API endpoints
│   └── schemas.py            # Pydantic models
├── static/
│   ├── index.html            # Frontend UI
│   ├── style.css             # Styling
│   └── script.js             # Client logic
└── data/
    ├── uploads/              # Uploaded documents
    └── chroma_db/            # Vector database
```

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Accessing API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI)

### Logging

Logs are output to console. Adjust log level in `config.py`:

```python
DEBUG = True  # Set to False for production
```

## Troubleshooting

### Issue: Model download takes too long
**Solution**: The embedding model (~90MB) downloads on first run. This is normal.

### Issue: CUDA/GPU errors
**Solution**: The app works fine on CPU. GPU is not required.

### Issue: "NVIDIA_API_KEY not set" warning
**Solution**: Add your API key to `.env` file. The app will run but won't generate LLM responses without it.

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: ChromaDB errors
**Solution**: Delete `data/chroma_db` folder and restart. The database will be recreated.

## Performance Tips

1. **Chunk Size**: Smaller chunks (500-800 tokens) work better for precise queries
2. **Overlap**: 15-20% overlap prevents context loss at chunk boundaries
3. **Top K**: Start with 3-5 results, increase for complex queries
4. **File Organization**: Group related documents for better context

## Security Considerations

- All document processing happens locally
- No documents are sent to external services except embeddings and LLM queries
- NVIDIA API receives only query text and retrieved context, not full documents
- Consider encrypting the `data/` directory for sensitive documents
- Use environment variables for API keys (never commit `.env`)

## Future Enhancements

- [ ] Multi-document comparison
- [ ] Export results to PDF
- [ ] User authentication
- [ ] Document versioning
- [ ] Custom metadata filters
- [ ] Batch query processing
- [ ] Advanced analytics dashboard

## License

This project is provided as-is for educational and commercial use.

## Contributing

Contributions welcome! Please feel free to submit issues and pull requests.

## Support

For issues and questions:
- Check the troubleshooting section above
- Review API documentation at `/docs`
- Open an issue on GitHub

## Acknowledgments

- Built with [LangChain](https://langchain.com/)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)
- Vector DB by [ChromaDB](https://www.trychroma.com/)
- LLM inference by [NVIDIA API](https://build.nvidia.com/)

---

**Note**: This is a demonstration project. For production use with sensitive legal documents, implement additional security measures including authentication, encryption, and access controls.

