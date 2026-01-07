import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re


class AdvancedWebNavAssistant:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        })

        self.soup = None
        self.base_url = ""

        # =========================
        # INTENT DEFINITIONS
        # =========================
        self.intent_map = {
            "create_project": ["create", "new", "project", "start", "build"],
            "login": ["login", "signin", "sign", "account"],
            "download": ["download", "install", "get"],
            "contact": ["contact", "support", "help"],
            "payment": ["payment", "pay", "fee", "charges"],
            "about": ["about", "company", "overview"]
        }

        # =========================
        # SYNONYMS (SMART NLP)
        # =========================
        self.synonyms = {
            "create": ["build", "make", "start"],
            "login": ["signin", "sign"],
            "download": ["install", "get"],
            "contact": ["support", "help"],
            "account": ["profile", "user"]
        }

        # =========================
        # STOPWORDS (NOISE REDUCTION)
        # =========================
        self.stopwords = {'the', 'is', 'at', 'which', 'on', 'a', 'an', 'and', 'or', 'for', 'to', 'of', 'in', 'with', 'i', 'me', 'my', 'how', 'can', 'do', 'does', 'what', 'where', 'it', 'this', 'that'}

        # =========================
        # RULE-BASED NAVIGATION FLOWS
        # =========================
        self.navigation_rules = {
            "create_project": [
                "Go to the website home page",
                "Look for buttons like 'New Project', 'Create', or 'Start'",
                "Choose the project or workspace type",
                "Proceed to the editor or dashboard"
            ],
            "login": [
                "Check the top-right corner of the website",
                "Click on 'Login' or 'Sign In'",
                "Enter your credentials to access your account"
            ],
            "download": [
                "Navigate to the Downloads or Resources section",
                "Select the required software or file",
                "Click the download button"
            ],
            "contact": [
                "Scroll to the footer or menu section",
                "Click on 'Contact Us' or 'Support'",
                "Use the available form or email information"
            ],
            "payment": [
                "Go to your account or billing section",
                "Check pricing or subscription details",
                "Proceed with payment options"
            ],
            "about": [
                "Navigate to the About or Company section",
                "Read the overview and mission details"
            ]
        }

    # =================================================
    # LOAD WEBSITE
    # =================================================
    def load_site(self, url):
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            self.soup = BeautifulSoup(response.text, "html.parser")
            self.base_url = response.url
            print("Website loaded and analyzed successfully.")
            return True
        except Exception as e:
            print("Failed to load website:", e)
            return False

    # =================================================
    # INTENT DETECTION
    # =================================================
    def detect_intent(self, query):
        query = query.lower()
        for intent, keywords in self.intent_map.items():
            if any(word in query for word in keywords):
                return intent
        return "general"

    # =================================================
    # TOKEN + SYNONYM EXPANSION
    # =================================================
    def expand_tokens(self, tokens):
        expanded = set(tokens)
        for token in tokens:
            if token in self.synonyms:
                expanded.update(self.synonyms[token])
        return expanded

    # =================================================
    # SMART CONTENT SEARCH (FALLBACK)
    # =================================================
    def smart_search(self, tokens):
        results = []

        for a in self.soup.find_all("a", href=True):
            text = a.get_text(" ", strip=True).lower()
            if not text:
                continue

            score = sum(1 for t in tokens if t in text)
            if score > 0:
                results.append({
                    "text": a.get_text(strip=True),
                    "url": urljoin(self.base_url, a["href"]),
                    "score": score
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:3]

    # =================================================
    # TEXT CONTENT SEARCH
    # =================================================
    def search_text_content(self, tokens):
        results = []
        
        for tag in self.soup.find_all(['h1', 'h2', 'h3', 'p', 'li']):
            text = tag.get_text(" ", strip=True)
            if len(text) < 30:
                continue

            score = sum(1 for t in tokens if t in text.lower())
            if score > 0:
                results.append({
                    "text": text,
                    "score": score
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:2]

    # =================================================
    # MAIN RESPONSE LOGIC
    # =================================================
    def get_response(self, user_query):
        if not self.soup:
            return "No website loaded."

        intent = self.detect_intent(user_query)

        tokens = set(re.findall(r"\w+", user_query.lower()))
        tokens = {t for t in tokens if t not in self.stopwords}
        tokens = self.expand_tokens(tokens)

        response = []

        # 🔹 RULE-BASED GUIDANCE (PRIMARY AI)
        if intent in self.navigation_rules:
            response.append("Here’s how you can proceed step by step:")
            for i, step in enumerate(self.navigation_rules[intent], 1):
                response.append(f"{i}. {step}")

            # 🔹 OPTIONAL SMART LINKS (SECONDARY)
            links = self.smart_search(tokens)
            if links:
                response.append("\nHelpful locations you may check:")
                for link in links:
                    response.append(f"- {link['text']} → {link['url']}")

            return "\n".join(response)

        # 🔹 FALLBACK SEARCH
        links = self.smart_search(tokens)
        text_hits = self.search_text_content(tokens)

        if links or text_hits:
            if links:
                response.append("I found these relevant sections:")
                for link in links:
                    response.append(f"- {link['text']} → {link['url']}")
            
            if text_hits:
                response.append("\nRelevant information from the page:")
                for hit in text_hits:
                    snippet = hit['text'][:200] + "..." if len(hit['text']) > 200 else hit['text']
                    response.append(f"- \"{snippet}\"")

            return "\n".join(response)

        return "I couldn't find specific information matching your query. Please try different keywords."


# =================================================
# RUN PROGRAM
# =================================================
if __name__ == "__main__":
    assistant = AdvancedWebNavAssistant()

    print("=== ADVANCED AI WEBSITE NAVIGATION ASSISTANT ===")
    print("Type 'exit' to quit\n")

    url = input("Enter website URL: ").strip()
    if assistant.load_site(url):
        while True:
            user_input = input("\nUser: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            print("\nAssistant:")
            print(assistant.get_response(user_input))