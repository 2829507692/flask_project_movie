from app import app
from flask_script import Manager,Server
from flask_migrate import MigrateCommand,Migrate
from app import mysql_db

Migrate(app, mysql_db)
manager = Manager(app)


if __name__ == '__main__':
    manager.add_command("db", MigrateCommand)
    # manager.add_command('runserver',Server())
    manager.run(default_command='runserver')