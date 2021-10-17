<h2>How to start this app:</h2>

- Step 1: Run docker sompose by command <b>docker-compose up --build</b>
- Step 2: Open browser and access to <b>localhost:8000/docs</b>
- Step 3: Change gmail environment variable to correct gmail. In order to enable sending email feature.
  - Open Dockerfile
  - Change value MAIL_FROM variable to your gmail. For example "yourgmail@gmail.com"
  - Change value MAIL_PASSWORD variable to your gmail password. For example "yourgmailpassword"
- Step 4: In order to view data from PostgreSQL Database, use PgAdmin and access to DB by following information:
  - POSTGRES PASSWORD: password
  - POSTGRES USER: postgres
  - POSTGRES DB: test
  - POSTGRES DB PORT: 5433
  - POSTGRES DB HOST: localhost
- Step 5: In order to view data from Redis database, follow below step:
  - Install Redis from this tutorial: arubacloud.com/tutorial/how-to-install-and-configure-redis-on-ubuntu-20-04.aspx
  - Type command "redis-cli -p 6380" to application's redis database.

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
  - Get all post information (paging, seaching), get single post information.
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
