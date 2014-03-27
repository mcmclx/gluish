# coding: utf-8

"""
Helper for databases.
"""

import logging

try:
    from MySQLdb.cursors import SSCursor
    import MySQLdb
except ImportError:
    logging.warn("MySQLdb seems missing: limited functionality.")

import sqlite3
import urlparse


class sqlite3db(object):
    """
    Simple context manager for sqlite3 databases. Commits everything at exit.

        with sqlite3db('/tmp/test.db') as cursor:
            query = cursor.execute('SELECT * FROM items')
            result = query.fetchall()
    """
    def __init__(self, path):
        self.path = path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.path)
        self.conn.text_factory = str
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        self.conn.commit()
        self.conn.close()


class mysqldb(object):
    """ Context manager for MySQL database access.

        with mysqldb('mysql://user:pass@host/db', stream=True) as cursor:
            query = cursor.execute('SELECT * FROM items')
            result = query.fetchall()

    """
    def __init__(self, url, stream=False, commit_on_exit=False):
        result = urlparse.urlparse(url, scheme='mysql')
        self.hostname = result.hostname
        self.username = result.username
        self.password = result.password
        self.database = result.path.strip('/')
        self.stream = stream
        self.commit_on_exit = commit_on_exit
        self.conn = None
        self.cursor = None

    def __enter__(self):
        if self.stream:
            self.conn = MySQLdb.connect(host=self.hostname, user=self.username,
                                        passwd=self.password, db=self.database,
                                        cursorclass=SSCursor)
        else:
            self.conn = MySQLdb.connect(host=self.hostname, user=self.username,
                                        passwd=self.password, db=self.database)

        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_class, exc, traceback):
        if self.commit_on_exit:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()
