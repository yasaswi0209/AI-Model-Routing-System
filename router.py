"""Explainable heuristic router. It is a baseline, not a trained classifier."""
import re

def route(question: str):
    q=question.lower(); reasons=[]
    if len(question.split()) >= 60: reasons.append('Long or detailed request')
    if '```' in question or re.search(r'\b(traceback|exception|debug|refactor|algorithm|sql query|complexity|architecture|compare|analy[sz]e|evaluate|optimi[sz]e)\b', q):
        reasons.append('Contains coding, analysis, or comparison terms')
    if question.count('?') >= 3: reasons.append('Contains several questions')
    return ('large' if reasons else 'small', reasons or ['Short request without complex keywords'])
