from final import *
import unittest

DBNAME = 'marvel.db'

class TestFinal(unittest.TestCase):
	
	def testCharDB(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
		statement = 'SELECT Name FROM Characters'
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertIn(('Mr. Negative',), result_list)
		self.assertEqual(len(result_list), 90)
		
		statement = '''
			SELECT Name FROM Characters
			GROUP BY Name ORDER BY Events DESC LIMIT 10
		'''
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertEqual(len(result_list), 10)
		self.assertEqual(result_list[2][0], 'Spider-Man')

		statement = '''
			SELECT Characters.Name, Links.Wiki FROM Characters JOIN Links 
			WHERE Links.MarvelId = Characters.MarvelId 
			GROUP BY Characters.Name ORDER BY Events DESC
		'''
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertEqual(len(result_list), 90)
		self.assertEqual(result_list[69][1], 'http://marvel.com/universe/Sunfire_(Age_of_Apocalypse)?utm_campaign=apiRef&utm_source=47fbbb8ce97fc46360c96f01d5179835')

		conn.close()

	def testLinkDB(self):
		conn = sqlite3.connect(DBNAME)
		cur = conn.cursor()
		statement = 'SELECT Name, Image FROM Links'
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertIn(('Mr. Negative', 'http://i.annihil.us/u/prod/marvel/i/mg/8/70/4c002efc322e3.jpg'), result_list)
		self.assertEqual(len(result_list), 90)

		statement = '''
			SELECT Name, Wiki, Image FROM Links
			ORDER BY Name DESC LIMIT 10
		'''
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertEqual(len(result_list), 10)
		self.assertEqual(result_list[2][0], 'X-23')
		self.assertEqual(result_list[6][1], 'http://marvel.com/universe/Vision_(Victor_Shade)?utm_campaign=apiRef&utm_source=47fbbb8ce97fc46360c96f01d5179835')
		self.assertEqual(result_list[9][2], 'http://i.annihil.us/u/prod/marvel/i/mg/6/c0/536165c7d94ae.jpg')

		statement = '''
			SELECT Links.Name, Links.Wiki, Characters.Comics FROM Links JOIN Characters ON Links.Id = Characters.Id
			WHERE (Characters.Comics < 250) LIMIT 10
		'''
		results = cur.execute(statement)
		result_list = results.fetchall()
		self.assertEqual(len(result_list), 10)
		self.assertEqual(result_list[2][0], 'Speedball (Robert Baldwin)')
		self.assertEqual(result_list[6][1], 'http://marvel.com/universe/Johnson,_Daisy?utm_campaign=apiRef&utm_source=47fbbb8ce97fc46360c96f01d5179835')
		self.assertEqual(result_list[9][2], 33)
		
		conn.close()


unittest.main()