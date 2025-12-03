# backend/app/cli.py (신규 파일)

import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User

@click.command('seed-db')
@with_appcontext
def seed_db_command():
    """Creates the default test user (user_id=1) if it doesn't exist."""
    
    # 1. user_id=1인 사용자가 이미 존재하는지 확인합니다.
    if User.query.get(1):
        click.echo('User ID 1 (testuser) already exists. Skipping seed.')
    else:
        # 2. 존재하지 않으면, 'testuser'를 생성합니다.
        try:
            new_user = User(user_id=1, username='testuser', email='test@test.com')
            new_user.set_password('test1234')
            db.session.add(new_user)
            db.session.commit()
            click.echo('✅ Successfully created user_id=1 (testuser).')
        except Exception as e:
            db.session.rollback()
            click.echo(f'❌ Failed to create test user: {e}')