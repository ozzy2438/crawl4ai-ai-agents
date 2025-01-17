import os
import openai
from typing import List, Dict, Optional
from embeddings import EmbeddingHandler
import logging
import httpx

class LLMChain:
    def __init__(self):
        self.embedding_handler = EmbeddingHandler()
        self.openai_client = openai.OpenAI()
        self.pplx_client = openai.OpenAI(
            api_key="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",
            base_url="https://api.perplexity.ai"
        )
        
    def get_perplexity_info(self, question: str, url: str) -> str:
        """Get additional information from Perplexity about the specific website content."""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that provides detailed information and relevant resources."
                },
                {
                    "role": "user",
                    "content": f"""Based on the question: {question}
                    
                    1. First, summarize the main points from {url}
                    2. Then, provide additional information and resources:
                       - Related YouTube channels and videos (with direct links)
                       - Similar articles and blog posts
                       - Research papers or documentation
                       - Community discussions and forums
                       - Tools and software related to the topic
                       
                    Format the response with clear headings and bullet points.
                    Make sure all links are properly formatted and accessible."""
                }
            ]
            
            try:
                response = self.pplx_client.chat.completions.create(
                    model="llama-3.1-sonar-large-128k-online",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=2048
                )
                
                if response.choices:
                    pplx_response = response.choices[0].message.content
                    
                    # Format the response
                    formatted_response = "### Additional Resources\n\n"
                    
                    # Split into sections
                    sections = pplx_response.split("\n\n")
                    for section in sections:
                        if "youtube" in section.lower():
                            formatted_response += "#### YouTube Resources\n" + section + "\n\n"
                        elif "article" in section.lower() or "blog" in section.lower():
                            formatted_response += "#### Related Articles\n" + section + "\n\n"
                        elif "paper" in section.lower() or "documentation" in section.lower():
                            formatted_response += "#### Research & Documentation\n" + section + "\n\n"
                        elif "discussion" in section.lower() or "forum" in section.lower():
                            formatted_response += "#### Community Resources\n" + section + "\n\n"
                        elif "tool" in section.lower() or "software" in section.lower():
                            formatted_response += "#### Tools & Software\n" + section + "\n\n"
                        else:
                            formatted_response += section + "\n\n"
                    
                    return formatted_response
                
                logging.error("No response from Perplexity API")
                return ""
                
            except Exception as e:
                logging.error(f"Perplexity API error: {str(e)}")
                return ""
                
        except Exception as e:
            logging.error(f"Error in get_perplexity_info: {str(e)}")
            return ""
    
    def format_context(self, similar_docs):
        context = []
        for doc in similar_docs:
            # Handle both ChromaDB Document objects and dictionary formats
            if isinstance(doc, dict):
                source = doc.get('metadata', {}).get('url', 'Unknown')
                title = doc.get('metadata', {}).get('title', '')
                date = doc.get('metadata', {}).get('date', '')
                content = doc.get('page_content', '') or doc.get('content', '')
            else:
                # Assume ChromaDB Document object
                source = doc.metadata.get('url', 'Unknown') if hasattr(doc, 'metadata') else 'Unknown'
                title = doc.metadata.get('title', '') if hasattr(doc, 'metadata') else ''
                date = doc.metadata.get('date', '') if hasattr(doc, 'metadata') else ''
                content = doc.page_content if hasattr(doc, 'page_content') else ''
            
            context.append(f"Source: {source}")
            if title:
                context.append(f"Title: {title}")
            if date:
                context.append(f"Date: {date}")
            context.append(f"Content: {content}\n")
        
        return "\n".join(context)
    
    def generate_response(self, context: str, question: str, url_filter: str) -> str:
        try:
            # Get base response from OpenAI
            messages = [
                {"role": "system", "content": "You are a helpful assistant that provides accurate information based on the given context. Only answer based on the information from the specified website. If you can't find relevant information in the context, say so clearly."},
                {"role": "user", "content": f"Context from {url_filter}:\n{context}\n\nQuestion: {question}\n\nAnswer based ONLY on the context above from {url_filter}. If the answer cannot be found in the context, say so clearly."}
            ]
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            base_response = response.choices[0].message.content
            
            # Get additional info from Perplexity
            pplx_info = self.get_perplexity_info(question, url_filter)
            
            if pplx_info:
                formatted_response = f"{base_response}\n\n---\n\n"
                formatted_response += pplx_info
                return formatted_response
            
            return base_response
            
        except Exception as e:
            logging.error(f"Error in generate_response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def query(self, question: str, url_filter: Optional[str] = None, top_k: int = 3) -> dict:
        try:
            similar_docs = self.embedding_handler.query_similar(question, url_filter=url_filter, top_k=top_k)
            
            if not similar_docs:
                return {"answer": f"I couldn't find any relevant information about that in {url_filter}. Try asking a different question or selecting another website.", "sources": []}
            
            context = self.format_context(similar_docs)
            answer = self.generate_response(context, question, url_filter)
            
            # Extract sources from documents
            sources = []
            for doc in similar_docs:
                if isinstance(doc, dict):
                    url = doc.get('metadata', {}).get('url')
                else:
                    url = doc.metadata.get('url') if hasattr(doc, 'metadata') else None
                
                if url and url not in sources:
                    sources.append(url)
            
            return {
                "answer": answer,
                "sources": sources
            }
            
        except Exception as e:
            return {"answer": f"Error: {str(e)}", "sources": []}

if __name__ == "__main__":
    # Example usage
    chain = LLMChain()
    
    # Example query
    question = "What information do you have about artificial intelligence?"
    result = chain.query(question)
    
    print("Question:", question)
    if result['answer']:
        print("\nAI Response:")
        print(result['answer'])
    print("\nRelevant Documents:")
    print(result['context'])
    print("\nSources:")
    for source in result['source_docs']:
        print(f"- {source['metadata']['url']}") 