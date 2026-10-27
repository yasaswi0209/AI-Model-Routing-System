import os, re, time
from dotenv import load_dotenv
import requests
from router import route
from storage import save

load_dotenv()
class ProviderError(Exception): pass

def pricing(tier, inp, out):
    """Only calculate when the user explicitly configured BOTH per-million prices."""
    a=os.getenv(f'{tier.upper()}_INPUT_USD_PER_MILLION','').strip(); b=os.getenv(f'{tier.upper()}_OUTPUT_USD_PER_MILLION','').strip()
    if not a or not b or inp is None or out is None: return None
    try:
        a,b=float(a),float(b)
        if a<0 or b<0: return None
        return (inp*a+out*b)/1_000_000
    except ValueError: return None

def generate(question, tier, demo=False):
    model=os.getenv('SMALL_MODEL','gemini-3.5-flash-lite') if tier=='small' else os.getenv('LARGE_MODEL','gemini-3.8-flash')
    if demo:
        return {'answer':'Demo response: The router selected the '+tier+' model. Add a Gemini API key and disable demo mode for a real AI answer.','model':'demo-'+tier,'input_tokens':None,'output_tokens':None}
    key=os.getenv('GEMINI_API_KEY','').strip()
    if not key: raise ProviderError('GEMINI_API_KEY is missing. Add it to .env or enable demo mode.')
    if not re.fullmatch(r'[A-Za-z0-9._-]+',model): raise ProviderError('Invalid model name in .env.')
    try:
        r=requests.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':key,'Content-Type':'application/json'},json={'contents':[{'parts':[{'text':question}]}]},timeout=60)
    except requests.RequestException as e: raise ProviderError('Could not reach the AI service. Check internet access and try again.') from e
    if not r.ok:
        if r.status_code==429: raise ProviderError('API quota or rate limit reached. Check your provider quota and try again later.')
        if r.status_code in (400,401,403): raise ProviderError(f'Provider rejected the request (HTTP {r.status_code}). Check the API key, model access and configuration.')
        raise ProviderError(f'AI service returned HTTP {r.status_code}. Check the selected model and provider status.')
    try:
        data=r.json(); answer=''.join(p.get('text','') for p in data['candidates'][0]['content']['parts']).strip()
        if not answer: raise ValueError('Empty answer')
    except (ValueError,KeyError,IndexError,TypeError) as e: raise ProviderError('The provider returned no usable answer; the prompt may have been blocked.') from e
    usage=data.get('usageMetadata',{}); return {'answer':answer,'model':model,'input_tokens':usage.get('promptTokenCount'),'output_tokens':usage.get('candidatesTokenCount')}

def process(question, mode='auto', demo=False):
    question=question.strip()
    if not question or len(question)>12000: raise ValueError('Enter a question between 1 and 12,000 characters.')
    if mode not in ('auto','small','large'): raise ValueError('Invalid routing mode.')
    proposed, reasons=route(question); tier=proposed if mode=='auto' else mode
    reason='; '.join(reasons) if mode=='auto' else 'Manually selected by user'
    t=time.perf_counter(); result=generate(question,tier,demo)
    record={'question':question,'answer':result['answer'],'tier':tier,'model':result['model'],'reason':reason,'mode':'demo' if demo else 'live','latency_ms':round((time.perf_counter()-t)*1000,1),'input_tokens':result['input_tokens'],'output_tokens':result['output_tokens'],'estimated_cost_usd':None if demo else pricing(tier,result['input_tokens'],result['output_tokens'])}
    save(record); return record
