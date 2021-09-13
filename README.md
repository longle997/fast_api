<h2>How to start this app:</h2>

- Step 1: run docker sompose by command <b>docker-compose up --build</b>
- Step 2: open browser and access to <b>localhost:8000/docs</b>
- Step 3: In order to view data from Database, use PgAdmin and access to DB by following information:
  - POSTGRES PASSWORD: password
  - POSTGRES USER: postgres
  - POSTGRES DB: test
  - POSTGRES DB PORT: 5433
  - POSTGRES DB HOST: localhost

<h2>Features of this application</h2>

- User:
  - Create user (email verification).
  - Get all user information, get single user information.
  - Login by email and password.
  - Change password, forgot password for user.


- Admin:
  - Activating user.
  - Delete user.


- Post:
  - Create post.
  - Get all post information, get single post information.
  - Delete post, update post.
  - Create post like.
  - Create, get, update, delete post comment.


<h2>Technologies were used in this application</h2>

- Python
- FastAPI, FastAPI_mail
- PostgreSQL, Alembic, SqlAchemy
- Redis
- Auth2
- Docker
