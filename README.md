# Crawl4AI Web Crawler & Chat 🕷️

A powerful web crawling and AI chat application that enables intelligent conversations with website content through vector embeddings and advanced language models.

## 🌟 Key Features

- **Advanced Web Crawling**
  - Configurable depth and breadth crawling
  - JavaScript rendering support
  - Smart content extraction
  - Automatic link discovery and filtering

- **Intelligent Data Processing**
  - Vector embeddings using SentenceTransformers
  - Efficient storage in Supabase with pgvector
  - ChromaDB integration for similarity search
  - Batch processing support

- **AI-Powered Chat Interface**
  - OpenAI GPT-4 integration
  - Perplexity AI for enhanced responses
  - Context-aware conversations
  - Source attribution and citations

- **Modern Web Interface**
  - Clean and responsive Streamlit UI
  - Dark mode support
  - Real-time crawling progress
  - Interactive chat experience

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Supabase account
- OpenAI API key
- Perplexity AI API key (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/crawl4ai-web-chat.git
cd crawl4ai-web-chat
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. Initialize the database:
```bash
# Run the schema.sql in your Supabase project
```

### Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Enter a URL to crawl in the Crawler tab
3. Wait for the crawling and processing to complete
4. Switch to the Chat tab to start asking questions about the crawled content

## 🔧 Configuration

Key configuration options in `.env`:

```env
OPENAI_API_KEY=your_openai_api_key
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
MAX_PAGES=200
BATCH_SIZE=10
```

## 🛠️ Architecture

- **Frontend**: Streamlit
- **Database**: Supabase with pgvector
- **Vector Store**: ChromaDB
- **Language Models**: OpenAI GPT-4, Perplexity AI
- **Embeddings**: SentenceTransformers

## 📚 Documentation

For detailed documentation on each component:

- [Crawler Configuration](docs/crawler.md)
- [Embedding System](docs/embeddings.md)
- [LLM Integration](docs/llm.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on how to submit pull requests, report issues, and contribute to the project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Streamlit](https://streamlit.io/) for the web framework
- [OpenAI](https://openai.com/) for GPT models
- [Supabase](https://supabase.com/) for vector database
- [SentenceTransformers](https://www.sbert.net/) for embeddings
- [ChromaDB](https://www.trychroma.com/) for vector storage

## 📞 Support

For support, please:
- Open an issue in the GitHub repository
- Join our [Discord community](https://discord.gg/yourdiscord)
- Contact us at support@yourdomain.com