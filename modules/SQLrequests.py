import aiosqlite
import asyncio
import json

class SQLtools():

    def __init__(self, DB_NAME):
        self.DB_NAME = DB_NAME
        self.directory = "./DataBase"
    
    async def get_tables(self):
        pass

    async def create_table(self, directory="./DataBase"):
        self.directory = directory
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            await db.execute('''CREATE TABLE IF NOT EXISTS quiz (user_id INTEGER PRIMARY KEY, question_index INTEGER, name STRING, questions STRING);''')
            await db.commit()

    async def update_quiz_index(self, user_id, index, name, questions=None):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            if questions==None:
                await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name) VALUES (?, ?, ?);', (user_id, index, name))
            elif type(questions) == int:
                result = None
                async with db.execute('SELECT questions FROM quiz WHERE user_id = (?);', (user_id, )) as cursor:
                    result = await cursor.fetchone()
                    result = json.loads(result)
                    result['questions'][index]['user_option'] = questions
                    result = json.dumps(result)
                await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name, questions) VALUES (?, ?, ?, ?);', (user_id, index, name, result))
            elif type(questions) == dict:
                questions = json.dumps(questions)
                await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name, questions) VALUES (?, ?, ?, ?);', (user_id, index, name, questions))
            else:
                await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name, questions) VALUES (?, ?, ?, ?);', (user_id, index, name, questions))
            await db.commit()

    async def get_quiz_index(self, user_id):
     async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
        async with db.execute('SELECT question_index FROM quiz WHERE user_id = (?);', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
    
    async def get_list_questions(self, user_id):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            async with db.execute('SELECT questions FROM quiz WHERE user_id = (?);',(user_id, )) as cursor:
                results = await cursor.fetchone()
                if results is not None:
                    return json.loads(results[0])
                else:
                    return 0
                
    async def get_question(self, user_id, index=None):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            async with db.execute('SELECT question_index, questions, name FROM quiz WHERE user_id = (?);',(user_id, )) as cursor:
                results = await cursor.fetchone()
                index = results[0] if index==None else index                
                await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name, questions) VALUES (?, ?, ?, ?);', (user_id, index, results[2], results[1]))               
                await db.commit()
                if index==len(json.loads(results[1])['questions']):
                    return (index, {"question":"Игра завершена","options":["начать заново","посмотреть статистику","ответы пользователя"]})
                results = json.loads(results[1])['questions'][index]
                return (index, results)
            
    async def set_option(self, user_id, option):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            async with db.execute('SELECT question_index, questions, name FROM quiz WHERE user_id = (?);',(user_id, )) as cursor:
                results = await cursor.fetchone() 
                name = results[2]         
                index = results[0]
                print(results)
                results = json.loads(results[1])
                if option in results['questions'][index]['options']:
                    results['questions'][index]['user_option'] = results['questions'][index]['options'].index(option)
                    index+=1
                    await db.execute('INSERT OR REPLACE INTO quiz (user_id, question_index, name, questions) VALUES (?, ?, ?, ?);', (user_id, index, name, json.dumps(results)))
                    await db.commit()
                    return True
                else:
                    return False
                
    async def get_statistic(self, user_id):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            async with db.execute('SELECT user_id, name, questions FROM quiz;') as cursor:
                results = await cursor.fetchall()
                r = ''
                for user in results:
                    name = ''
                    if user_id==user[0]:
                        name = 'Ваш'
                    else:
                        name = user[1]
                    questions = json.loads(user[2])["questions"]
                    true = 0
                    for question in questions:
                        if question['user_option']==question["correct_option"]:
                            true+=1
                    r+= f"{name} {true}/{len(questions)}\n"
                return r
    
    async def get_positions(self, user_id):
        async with aiosqlite.connect(f"{self.directory}/{self.DB_NAME}") as db:
            async with db.execute('SELECT questions FROM quiz WHERE user_id=(?);',(user_id,)) as cursor:
                results = await cursor.fetchone()
                r = ''
                for question in json.loads(results[0])['questions']:
                    if question['user_option'] == -1:
                        continue
                    r+=f"{question['question']} - {question['options'][question['user_option']]}\n"
                return r
