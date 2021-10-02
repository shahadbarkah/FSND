import os
import re
from flask import Flask, request, abort, jsonify
from flask.globals import current_app
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request,questions):
  page=request.args.get('page',1,type=int)
  start=(page-1)*QUESTIONS_PER_PAGE
  end=start+QUESTIONS_PER_PAGE
  formated_questions=[question.format() for question in questions]
  current_questions=formated_questions[start:end]
  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app,resources={r"/*":{"origins":"*"}})
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,authorization, true')
    response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH,DELETE, OPTIONS')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def categories():
    category=Category.query.order_by(Category.id).all()
    formated_category={categories.id: categories.type for categories in category}
    
    if len(category)==0:
      abort(404)
          
    return jsonify({
      "Success":True,
      "categories":formated_category
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_questions():
    question=Question.query.order_by(Question.id).all()
    current_questions=paginate_questions(request,question)
    
    if len(current_questions)==0:
      abort(404)
      
    categories=Category.query.order_by(Category.id).all()
    formated_category={category.id:category.type for category in categories}
    
    return jsonify({
      "questions":current_questions,
      "totalQuestions":len(question),
      "categories":formated_category,
      "currentCategory":None
    })
    
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>',methods=['DELETE'])
  def delete_question(question_id):
    try:
      question=Question.query.filter(Question.id==question_id).one_or_none()
      
      if question is None:
        abort(404)
        
      question.delete()
      
      return jsonify({
        "success":True
      })
    except:
      abort(422)
  
  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions',methods=['POST'])
  def add_question():
    body=request.get_json()
    try:
      new_question=Question(question=body.get('question'),answer=body.get('answer'),
                            difficulty=body.get('difficulty'),category=body.get('category'))
      new_question.insert()
      return jsonify({
        "success":True
      })
    except:
      abort(422)
  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search',methods=['POST'])
  def search_question():
    body=request.get_json()
    search_term=body.get('searchTerm')
    try:
      question=Question.query.filter(Question.question.ilike('%'+search_term+'%')).all()
      current_questions=paginate_questions(request,question)
    except:
      abort(422)   
       
    return jsonify({
      "questions":current_questions,
      "totalQuestions":len(question),
      "currentCategory":None
    })

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def question_by_category(category_id):
    category=Category.query.filter(Category.id==category_id).one_or_none()
    current_category=category.type
    questions=Question.query.filter(Question.category==category_id).all()
    current_questions=paginate_questions(request,questions)
    if len(questions)==0:
      abort(404)
    
    
    return jsonify({
      "success":True,
      "questions":current_questions,
      "totalQuestions":len(questions),
      "currentCategory":current_category
    })

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes',methods=['POST'])
  def quizze():
    body=request.get_json()
    category=body.get('quiz_category')
    previous_questions=body.get('previous_questions')
    
    try:
      if category['id']==0 and len(previous_questions)>0:
        questions=Question.query.filter(Question.id.notin_(previous_questions)).all()
      elif category['id']!=0 and len(previous_questions)>0:
        questions=Question.query.filter(Question.category==category['id'],Question.id.notin_(previous_questions)).all()
      elif category['id']!=0 and len(previous_questions)==0:
        questions=Question.query.filter(Question.category==category['id']).all()  
      else:
        questions=Question.query.all()
      
      formated_questions=[q.format() for q in questions]
            
      if len(formated_questions)>0:
        random_question=random.choice(formated_questions)
        return jsonify({
              'success':True,
              'question':random_question,
              'previous_questions':previous_questions
                })
      else:
        return jsonify({
              'success':True,
              'question':None,
              'previous_questions':previous_questions
                })
    except:
     abort(422)      

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False, 
      "error": 404,
      "message": "Not found"
        }), 404
    
  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
     "success": False, 
     "error": 422,
     "message": "unprocessable"
        }), 422
    
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
     "success": False,
      "error": 400,
      "message": "bad request"
      }), 400
    
  return app

    