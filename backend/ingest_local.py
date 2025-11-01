import os, time, json
import requests
from bs4 import BeautifulSoup
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def fetch_text(url):
    try:
        r = requests.get(url, timeout=15, headers={"User-Agent":"perplexity-demo-bot/1.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for s in soup(['script','style','noscript']): s.decompose()
        paras = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
        return '\n'.join(paras)
    except Exception as e:
        print('fetch error', e)
        return ''

def chunk_text(text, max_words=300, overlap=50):
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        chunk = words[i:i+max_words]
        chunks.append(' '.join(chunk))
        i += max_words - overlap
    return chunks

def index_urls(urls, out_path='../data/embeddings.json'):
    out = []
    for url in urls:
        txt = fetch_text(url)
        if not txt:
            continue
        chunks = chunk_text(txt)
        for i, ch in enumerate(chunks):
            resp = openai.Embedding.create(model='text-embedding-3-small', input=[ch])
            emb = resp['data'][0]['embedding']
            item = {'id': f'{url}#{i}', 'url': url, 'title': url, 'text': ch, 'embedding': emb}
            out.append(item)
            time.sleep(0.35)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f)
    print('Wrote', out_path, 'entries:', len(out))

if __name__ == '__main__':
    URLS = [
        'https://en.wikipedia.org/wiki/Artificial_intelligence',
        'https://en.wikipedia.org/wiki/Machine_learning',
        'https://en.wikipedia.org/wiki/Natural_language_processing'
    ]
    index_urls(URLS)
