import argparse
import sys
from typing import List, Dict
from crawler import Crawler
from embeddings import EmbeddingHandler
from llm_chain import LLMChain

def process_crawled_data(crawled_data: List[Dict[str, str]]) -> bool:
    """Process and validate crawled data before storing embeddings."""
    if not crawled_data:
        print("No data was crawled. Please check the URL and try again.")
        return False
    
    valid_data = []
    for item in crawled_data:
        if item.get('content') and len(item['content'].strip()) > 100:  # Minimum content length
            valid_data.append(item)
        else:
            print(f"Skipping document from {item.get('url')} due to insufficient content")
    
    if not valid_data:
        print("No valid content was found in the crawled data.")
        return False
    
    print(f"\nFound {len(valid_data)} valid documents")
    
    try:
        print("\nProcessing and storing embeddings...")
        embedding_handler = EmbeddingHandler()
        embedding_handler.process_and_store(valid_data)
        print("Embeddings stored successfully")
        return True
    except Exception as e:
        print(f"Error processing embeddings: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Web Crawler and Document Retrieval System')
    parser.add_argument('--crawl', type=str, help='URL to crawl')
    parser.add_argument('--query', type=str, help='Question to ask the system')
    args = parser.parse_args()

    if args.crawl:
        try:
            print(f"Starting to crawl: {args.crawl}")
            crawler = Crawler()
            crawled_data = crawler.crawl(args.crawl)
            
            if not process_crawled_data(crawled_data):
                sys.exit(1)
                
        except Exception as e:
            print(f"Error during crawling: {str(e)}")
            sys.exit(1)

    if args.query:
        try:
            print(f"\nProcessing query: {args.query}")
            chain = LLMChain()
            result = chain.query(args.query)
            
            if result.get('answer'):
                print("\nAI Response:")
                print(result['answer'])
                print("\n---")
            
            if result.get('context'):
                print("\nRelevant Documents:")
                print(result['context'])
                if result.get('sources'):
                    print("\nSources:")
                    for source in result['sources']:
                        print(f"- {source}")
            else:
                print("\nNo relevant information found for your query.")
                
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    main() 