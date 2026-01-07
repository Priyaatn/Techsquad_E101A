import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re

class WebNavAssistant:
    def __init__(self):
        self.session = requests.Session()
        # Mimic a real browser to avoid being blocked
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        self.soup = None
        self.base_url = ""

    def load_site(self, url):
        """Loads the website and parses its structure."""
        url = url.strip(' "\'')
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        print(f"Connecting to {url}...")
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, 'html.parser')
            self.base_url = response.url
            print("Site loaded successfully. I have analyzed the navigation structure and content.")
            return True
        except Exception as e:
            print(f"Failed to load site: {e}")
            return False

    def get_response(self, user_query):
        """
        Analyzes the user's natural language query to find relevant links or text.
        """
        if not self.soup:
            return "No site loaded."

        query_lower = user_query.lower().strip()
        # Filter out common stopwords to improve keyword matching accuracy
        stopwords = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in', 'with', 'i', 'me', 'my'}
        query_tokens = set(re.findall(r'\w+', query_lower)) - stopwords

        if not query_tokens and not query_lower:
            return "I didn't catch that. Could you ask differently?"

        candidates = []

        # 1. Search Navigation Links (Prioritize finding the "location")
        for a in self.soup.find_all('a', href=True):
            link_text = a.get_text(" ", strip=True)
            href = a['href'].strip()
            
            if href.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue

            link_title = a.get('title', '')
            full_link_text = (link_text + " " + link_title).lower()

            if not link_text:
                continue
            
            score = 0
            # Bonus for exact phrase match
            if query_lower in full_link_text:
                score += 50
            
            # Score based on keyword matches
            matches = sum(1 for token in query_tokens if token in full_link_text)
            score += matches * 10
            
            if score > 0:
                candidates.append({
                    'type': 'link',
                    'text': link_text,
                    'url': urljoin(self.base_url, href),
                    'score': score
                })

        # 2. Search Page Content
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = tag.get_text(" ", strip=True)
            if len(text) < 20: continue # Skip short snippets

            text_lower = text.lower()
            score = 0
            
            if query_lower in text_lower:
                score += 40
            
            matches = sum(1 for token in query_tokens if token in text_lower)
            score += matches * 10
            
            if score > 0:
                candidates.append({
                    'type': 'text',
                    'content': text,
                    'score': score
                })

        # Sort candidates by score
        candidates.sort(key=lambda x: x['score'], reverse=True)
        
        if not candidates:
            return "I couldn't find information matching your query on this page. Try using different keywords."

        # Formulate Response
        response_parts = []
        
        # Get top results (limit to top 3 to be specific but comprehensive)
        top_links = [c for c in candidates if c['type'] == 'link'][:3]
        top_text = [c for c in candidates if c['type'] == 'text'][:1]

        if top_links:
            response_parts.append("I found these relevant locations:")
            for link in top_links:
                response_parts.append(f"- {link['text']}: {link['url']}")
        
        if top_text:
            if top_links:
                response_parts.append("\nI also found this related information:")
            else:
                response_parts.append("I found this information:")
            
            snippet = top_text[0]['content'][:300]
            if len(top_text[0]['content']) > 300:
                snippet += "..."
            response_parts.append(f"\"{snippet}\"")
        
        return "\n".join(response_parts)

if __name__ == "__main__":
    assistant = WebNavAssistant()
    print("=== AI Website Navigation Assistant ===")
    print("This tool helps you navigate complex websites using natural language.")
    
    print("\nHere are some popular Open Source websites you can try:")
    print("1. Python:        https://www.python.org")
    print("2. Linux Kernel:  https://www.kernel.org")
    print("3. Apache:        https://httpd.apache.org")
    print("4. GNU Project:   https://www.gnu.org")
    print("5. Wikipedia:     https://www.wikipedia.org")

    print("\nHere are some Banking websites you can try:")
    print("6. Chase:         https://www.chase.com")
    print("7. Bank of America: https://www.bankofamerica.com")
    print("8. HDFC Bank:     https://www.hdfcbank.com")

    print("\nHere are some Commercial/Tech websites you can try:")
    print("9. Microsoft:     https://www.microsoft.com")
    print("10. Apple:        https://www.apple.com")
    print("11. Amazon:       https://www.amazon.com")

    url = input("\nEnter website URL to start (copy one from above or type your own): ").strip(' "\'')
    if url and assistant.load_site(url):
        print("\nSystem Ready. Ask me anything about the website! (Type 'quit' to exit)")
        while True:
            query = input("\nUser: ")
            if query.lower() in ['quit', 'exit']:
                break
            print(f"Assistant: {assistant.get_response(query)}")