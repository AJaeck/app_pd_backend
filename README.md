Here’s how to set up and use Flask-Migrate step-by-step:

Step 1: Install Flask-Migrate

First, you need to install Flask-Migrate along with its dependencies. If you haven’t installed it yet, you can do so using pip:

bash

`pip install Flask-Migrate`

Step 2: Configure Flask-Migrate in Your Application

In your Flask application, you need to import and initialize Flask-Migrate. Here’s how you can set it up:

`python

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///path_to_your_database.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Define your models (e.g., User, Results)

if __name__ == '__main__':
    app.run(debug=True)`

Step 3: Initialize the Migration Repository

Flask-Migrate uses a migration repository to keep track of database migrations. To create this repository, which includes the necessary configuration files, run the following command in your terminal:

`flask db init`

This command creates a new directory named migrations in your application directory. Inside, you'll find migration scripts that will be generated in the next steps.
Step 4: Create a Migration Script

Whenever you make changes to your database models, you need to generate a new migration script. Flask-Migrate generates these scripts automatically based on the differences it detects between your database schema and your SQLAlchemy models.

Run the following command to automatically generate a migration script:

`flask db migrate -m "Initial migration"`  # You can customize the message describing the migration

This command will detect changes in your models and create a script in the migrations/versions directory that describes those changes.
Step 5: Apply the Migration to the Database

To apply the migration (i.e., to make the schema changes to your actual database), run:

`flask db upgrade`

This command applies the migration scripts in the correct sequence to modify your database schema without losing data.

Step 6: Manage Migrations

You can manage your database schema using these commands:

    flask db downgrade: Reverts the last migration, which can be useful if you need to undo a migration applied to your database.
    flask db history: Shows a history of migrations.
    flask db current: Displays the current revision for the database.

Additional Considerations

    Environment Variables: Flask-Migrate reads from the FLASK_APP environment variable to know which application to run and migrate. Make sure to set FLASK_APP=your_application_file.py before running migration commands if your entry file is not named app.py.
    Deployment: When deploying your application, remember to run flask db upgrade as part of your deployment process to apply any pending migrations to the production database.

Using Flask-Migrate helps you manage database schema changes systematically and safely, preserving your data across changes and making your development workflow much more manageable.