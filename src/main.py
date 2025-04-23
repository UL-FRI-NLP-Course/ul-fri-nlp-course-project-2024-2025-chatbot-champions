from crawler import search_news, compare_query_results
import time

if __name__ == "__main__":
    # query = input("Enter your question: ").strip()
    # if not query:
    #     print("Please enter a valid question.")
    #     return

    # compare_query_results("Luka Dončič", "Dončič")

    query = "Luka Dončič"
    # Extract keywords from the question
    start_time = time.time()
    articles = search_news(query, per_page=20)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time:.2f} seconds")
    print(f"Found {len(articles)} articles for the query '{query}':")
