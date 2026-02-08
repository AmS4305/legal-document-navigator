# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your NVIDIA API key
# Get one free at: https://build.nvidia.com/
```

### 3. Run the Application
```bash
python main.py
```

### 4. Open Your Browser
Navigate to: `http://localhost:8000`

## 📝 First Steps

### Upload a Document
1. Click the upload area or drag & drop a file
2. Supported: PDF, DOCX, TXT (max 50MB)
3. Wait for processing confirmation

### Ask a Question
1. Type your question in the search box
2. Try example queries like:
   - "Find all termination clauses"
   - "What are the payment terms?"
   - "Summarize the key points"
3. Click Search

### Review Results
- Read the AI-generated answer
- Check source citations
- View confidence scores

## 🔑 Get Your Free NVIDIA API Key

1. Go to https://build.nvidia.com/
2. Create a free account
3. Select "Llama 3.1 Nemotron" or similar model
4. Click "Get API Key"
5. Copy the key to your `.env` file

## 📚 Example Use Cases

**Contract Analysis**
- "Find all liability limitations across contracts"
- "What are the termination conditions?"
- "List all payment due dates"

**Case Research**
- "Find cases mentioning intellectual property"
- "Summarize precedents for contract disputes"
- "What are the key arguments in Smith vs. Jones?"

**Document Discovery**
- "Which documents discuss confidentiality?"
- "Find all mentions of indemnification"
- "What are the governing law clauses?"

## 🛠️ Troubleshooting

**"NVIDIA_API_KEY not set" warning?**
→ Add your API key to `.env` file

**Import errors?**
→ Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

**Slow first query?**
→ Normal! Embedding model downloads on first run (~90MB)

## 📖 Learn More

- Full documentation: See `README.md`
- API docs: http://localhost:8000/docs
- Configuration: Edit `config.py`

## 💡 Pro Tips

1. **Better Results**: Upload multiple related documents for richer context
2. **Specific Queries**: Ask specific questions for more precise answers
3. **Document Size**: Break very large documents into chapters/sections
4. **Chunk Size**: Adjust `CHUNK_SIZE` in config.py for your use case

---

**Need Help?** Check the full README.md or API documentation at `/docs`
