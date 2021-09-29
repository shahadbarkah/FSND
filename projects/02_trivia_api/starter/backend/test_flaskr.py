import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import null

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','As123a123','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        
        self.new_question={'question':' What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?','answer':'Edward Scissorhands',
                                                  'difficulty':3,'category':5}
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['Success'],True)
        self.assertTrue(data['categories'])
        self.assertTrue(len(data['categories']))
        
    def test_delete_question(self):    
        res=self.client().delete('/questions/26')
        data=json.loads(res.data)
        
        question=Question.query.filter(Question.id==3).one_or_none()
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertIsNone(question)
    
    def test_add_question(self):
        res=self.client().post('/questions',json=self.new_question)
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        
    def test_search_question_with_result(self):
        res=self.client().post('/questions/search',json={'searchTerm':'Who invented Peanut Butter?'})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['totalQuestions'],1)
        self.assertTrue(data['questions'])
    
    def test_get_question_by_category(self):
        res=self.client().get('/categories/2/questions')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['totalQuestions'],4)
        self.assertTrue(data['questions'])   
    
    def test_quizze(self):
        res=self.client().post('/quizzes',json={'quiz_category': {"type": "History", "id": 4}
                                                ,'previous_questions':["2"]})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
             
            
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()