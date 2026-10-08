"""Regression checks for retrieval and calendar behavior, not claims of accuracy."""
import json
import unittest
from datetime import date
from pathlib import Path
from chatbot import FAQBot, countdown

class ChatbotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bot = FAQBot(json.loads((Path(__file__).parent / 'data/faqs.json').read_text()))

    def test_held_out_phrasings(self):
        cases = {'I need my admit card': 'hall', 'How much money for revaluation?': 'fee', 'download semester marks': 'results', 'exam registration last date': 'registration', 'semester examinations begin': 'semester', 'request copy of answer script': 'photocopy', 'attendance eligibility': 'attendance'}
        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertEqual(self.bot.answer(question).get('id'), expected)

    def test_unknown_and_mixed_queries(self):
        for question in ['', 'hello', 'What is the weather today?', 'exam banana spaceship purple', 'Tell me the library opening hours']:
            with self.subTest(question=question):
                self.assertFalse(self.bot.answer(question)['matched'])

    def test_ambiguous_query(self):
        self.assertFalse(self.bot.answer('hall ticket exam registration')['matched'])

    def test_related_questions(self):
        result = self.bot.answer('How can I apply for revaluation?')
        self.assertEqual([item['id'] for item in result['suggestions']], ['fee', 'photocopy', 'results'])

    def test_countdown_boundaries(self):
        event = {'label': 'Test', 'date': '2026-11-16'}
        for today, days, status in [(date(2026,10,8),39,'39 days to go'), (date(2026,11,15),1,'Tomorrow'),(date(2026,11,16),0,'Today'),(date(2026,11,17),-1,'1 day ago')]:
            with self.subTest(today=today):
                result=countdown(event,today)
                self.assertEqual((result['days'],result['status']), (days,status))

    def test_training_questions_and_references(self):
        for faq in self.bot.faqs.values():
            for related in faq['related']:
                self.assertIn(related,self.bot.faqs)
            if faq['event']:
                self.assertIn(faq['event'],self.bot.data['events'])
            for question in faq['questions']:
                with self.subTest(question=question):
                    self.assertEqual(self.bot.answer(question).get('id'),faq['id'])

if __name__ == '__main__':
    unittest.main()
