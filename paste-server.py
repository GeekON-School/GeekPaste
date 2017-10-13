import tornado.ioloop
import tornado.web
import sqlite3
import random
import string
import os

DB_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
							     'database.sqlite')

def get_id():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.get_argument('id', None)
        if id is None:
            self.render('index.html')
        else:
            try:
                con = sqlite3.connect(DB_PATH)
                cur = con.cursor()
                cur.execute('SELECT * FROM codes WHERE id = ?', [id])
                code = cur.fetchone()
                if code == None:
                    raise Exception("error")
                con.close()
                self.render('codepage.html', record=code)
            except Exception as e:
                print(e)
                self.render('notfound.html')
    def post(self):
        lang = self.get_argument('lang', None)
        code = self.get_argument('code', None)
        if lang is None or code is None:
            self.redirect('/')
        else:
            con = sqlite3.connect(DB_PATH)
            cur = con.cursor()

            id = ''
            while True:
                id = get_id()
                cur.execute('SELECT COUNT(*) FROM codes WHERE id = ?', [id])
                if cur.fetchone()[0] == 0:
                    break

            cur.execute('INSERT INTO codes (id, lang, code) VALUES (?,?,?)', [id, lang, code])
            con.commit()
            con.close()
            self.redirect('/?id={}'.format(id))

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8084)
    tornado.ioloop.IOLoop.current().start()