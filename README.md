# Flask-Vanilla Demo

This is a demo website that uses
[Flask][flask] to serve pages styled with
[Vanilla Framework][vanilla]. I worked on this while
learning Vanilla and going through the
[_Flask Framework Cookbook_][flask-cookbook].

## What it implements

- Create & view products and categories
  - uses [Vanilla Framework][vanilla] for front end styling and [Flask-WTForms][flask-wtforms] for form processing
  - uses [Flask-SQLAlchemy][flask-sqlalchemy] and [Flask-Migrate][flask-migrate] to store & manage data in the database
- User accounts with authentication
  - uses [Flask-Login][flask-login] for local registration and [Flask-Dance][flask-dance] for logging in via GitHub
- RESTful API to create, update, and delete products
  - uses [Flask-RESTful][flask-restful]
- Admin interface to manage the database through the site
  - uses [Flask-Admin][flask-admin]

## Project setup and running

Copy `.env` to `.env.local` and modify it with your configuration settings:

```bash
export SECRET_KEY=YourSecretKey
export FLASK_ENV=development
export GITHUB_OAUTH_CLIENT_ID=YourGithubOauthClienId
export GITHUB_OAUTH_CLIENT_SECRET=YourGithubOauthClientSecret
```

To allow user authentication via GitHub,
[create an OAuth app][github-create-app] on GitHub and use
the client ID and secret to set `GITHUB_OAUTH_CLIENT_ID` and
`GITHUB_OAUTH_CLIENT_SECRET`.

Create a virtual environment and install requirements:

```bash
$ virtualenv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

Run the server:

```bash
$ source .env.local
$ flask run --cert=adhoc
```

You should be able to access the site at https://localhost:5000.

> **Note:** OAuth2 integration with GitHub requires HTTPS to work, so the above
> command uses the `--cert=adhoc` option to generate self-signed certificates
> for development. You can leave this option off and access the site over plain
> HTTP if you don't care about using GitHub for user authentication.

## Deployment

### Heroku button

Click the button below to deploy to Heroku.

[![Deploy to Heroku][heroku-button]][heroku-deploy]

### Heroku CLI

TODO

[flask]: https://flask.palletsprojects.com/
[vanilla]: https://vanillaframework.io/
[flask-cookbook]: https://www.packtpub.com/product/flask-framework-cookbook-second-edition/9781789951295
[flask-wtforms]: https://flask-wtf.readthedocs.io/
[flask-sqlalchemy]: https://flask-sqlalchemy.palletsprojects.com/
[flask-migrate]: https://flask-migrate.readthedocs.io/
[flask-login]: https://flask-login.readthedocs.io/
[flask-dance]: https://flask-dance.readthedocs.io/
[flask-restful]: https://flask-restful.readthedocs.io/
[flask-admin]: https://flask-admin.readthedocs.io/
[github-create-app]: https://docs.github.com/en/developers/apps/building-oauth-apps/creating-an-oauth-app
[heroku-button]: https://www.herokucdn.com/deploy/button.svg
[heroku-deploy]: https://heroku.com/deploy?template=https://github.com/mrgnr/flask-vanilla-demo/tree/heroku
