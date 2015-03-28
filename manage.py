# encoding: utf-8

from flask.ext.script import Manager

from webapp import app
from webapp import util

manager = Manager(app)

@manager.command
def sync():
  util.sync()

@manager.command
def test():
  util.test()

if __name__ == "__main__":
  manager.run()