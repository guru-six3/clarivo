"""Small, inspectable TF-IDF retrieval engine. No generative AI or external API."""
import math
import re
from collections import Counter
from datetime import date

STOP_WORDS = set('a an the is are was were do does did i my me you your we our can could would should please how what when where to of for in on at and it be will'.split())


def tokenize(text):
    """Lowercase, extract words, then remove common grammatical words."""
    return [word for word in re.findall(r'[a-z0-9]+', text.lower()) if word not in STOP_WORDS]


def countdown(event, today):
    """Return days until an ISO date, preserving today's and past-event states."""
    days = (date.fromisoformat(event['date']) - today).days
    if days > 1:
        status = f'{days} days to go'
    elif days == 1:
        status = 'Tomorrow'
    elif days == 0:
        status = 'Today'
    elif days == -1:
        status = '1 day ago'
    else:
        status = f'{abs(days)} days ago'
    return {**event, 'days': days, 'status': status}


class FAQBot:
    def __init__(self, data):
        self.data = data
        self.faqs = {faq['id']: faq for faq in data['faqs']}
        # Every question variation is a document with a known FAQ owner.
        self.documents = [(faq['id'], tokenize(question)) for faq in data['faqs'] for question in faq['questions']]
        frequency = Counter(word for _, words in self.documents for word in set(words))
        count = len(self.documents)
        # Smoothed IDF: rare words receive more weight than common words.
        self.idf = {word: math.log((1 + count) / (1 + occurrences)) + 1 for word, occurrences in frequency.items()}
        self.vectors = [(owner, self.vector(words)) for owner, words in self.documents]

    def vector(self, words):
        counts = Counter(word for word in words if word in self.idf)
        weights = {word: count * self.idf[word] for word, count in counts.items()}
        length = math.sqrt(sum(value * value for value in weights.values()))
        return {word: value / length for word, value in weights.items()} if length else {}

    def answer(self, question, today=None):
        today = today or date.today()
        words = tokenize(question)
        query = self.vector(words)
        scores = {}
        for owner, vector in self.vectors:
            # Unit-length vectors make the dot product equal cosine similarity.
            similarity = sum(value * vector.get(word, 0) for word, value in query.items())
            scores[owner] = max(scores.get(owner, 0), similarity)
        ranked = sorted(scores.items(), key=lambda pair: pair[1], reverse=True)
        owner, score = ranked[0]
        runner_up = ranked[1][1] if len(ranked) > 1 else 0
        coverage = sum(word in self.idf for word in words) / len(words) if words else 0
        # Similarity is not a probability. Reject weak, ambiguous, or mostly unknown text.
        accepted = score >= self.data['threshold'] and coverage >= 0.5 and score - runner_up >= self.data['ambiguity_margin']
        if not accepted:
            return {'matched': False, 'answer': 'I could not confidently match that question. I can help with semester exams, hall tickets, revaluation, results and exam rules. Try a question below, or contact the examination office for an official answer.', 'score': round(score, 3), 'suggestions': [{'id': faq['id'], 'question': faq['questions'][0]} for faq in list(self.faqs.values())[:3]], 'event': None}
        faq = self.faqs[owner]
        event = self.data['events'].get(faq.get('event'))
        return {'matched': True, 'id': owner, 'topic': faq['topic'], 'answer': faq['answer'], 'score': round(score, 3), 'suggestions': [{'id': related, 'question': self.faqs[related]['questions'][0]} for related in faq['related']], 'event': countdown(event, today) if event else None}
