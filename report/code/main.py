from crawler import search_news
import time
def main():
    # query = input("Enter your question: ").strip()
    # if not query:
    #     print("Please enter a valid question.")
    #     return
    query = "dončič"
    # Extract keywords from the question
    start_time = time.time()
    articles = search_news(query)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Found {len(articles)} articles for the query '{query}':")

if __name__ == "__main__":
    main()
