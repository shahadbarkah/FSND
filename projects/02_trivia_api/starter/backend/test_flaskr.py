import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import null
from dotenv import load_dotenv

from flaskr import create_app
from models import setup_db, Question, Category
load_dotenv()

class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.username= os.getenv('DB_USER')
        self.password=os.getenv('DB_PASSWORD')
        self.host=os.getenv('DB_HOST')
        self.database_path = "postgresql://{}:{}@{}/{}".format(self.username,self.password,self.host, self.database_name)
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
        
        
    def test_404_get_categories(self):
        res=self.client().get('/categories/900')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'Not found')
        self.assertEqual(data['error'], 404)
        self.assertFalse(data['success'])
            
    def test_delete_question(self):    
        res=self.client().delete('/questions/75')
        data=json.loads(res.data)
        
        question=Question.query.filter(Question.id==75).one_or_none()
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertIsNone(question)
    
    def test_422_delete_question(self):
        res=self.client().delete('/questions/3000')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])
        
    def test_add_question(self):
        res=self.client().post('/questions',json=self.new_question)
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
       
    # The category(id) of the question is not correct and not in the database    
    def test_422_add_question(self):
        res=self.client().post('/questions',json={'question':'1+1?','answer':'2','difficulty':1,'category':10})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success']) 
        
        
    def test_search_question_with_result(self):
        res=self.client().post('/questions/search',json={'searchTerm':'Who invented Peanut Butter?'})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['totalQuestions'],1)
        self.assertTrue(data['questions'])
        
    def test_search_question_without_result(self):
        res=self.client().post('/questions/search',json={'searchTerm':'50000'})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['totalQuestions'],0)
        self.assertFalse(data['questions'])
    
    def test_get_question_by_category(self):
        res=self.client().get('/categories/2/questions')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['totalQuestions'],4)
        self.assertTrue(data['questions'])   
    
    def test_404_get_question_by_categoty(self):
        res=self.client().get('/categories/44/questions')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['message'],'Not found')
        self.assertEqual(data['error'], 404)
        self.assertFalse(data['success'])
        
        
    def test_quizze(self):
        res=self.client().post('/quizzes',json={'quiz_category': {"type": "History", "id": 4}
                                                ,'previous_questions':["2"]})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
        
        
    def test_422_test_quizze(self):         
        res=self.client().post('/quizzes',json={'quiz_category': {"type": "History", "id": 'aaa'}
                                                ,'previous_questions':["2"]})
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['message'],'unprocessable')
        self.assertEqual(data['error'], 422)
        self.assertFalse(data['success'])     
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()