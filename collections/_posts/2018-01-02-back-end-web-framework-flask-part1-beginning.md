---
layout: post
title: "Back-end Web Framework: Flask (Part 1: Beginning)"
date: 2018-01-20
summary: "Flask is a micro web framework written in Python..."
categories: software-engineering, programming, python, flask
permalink: back-end-web-framework-flask-beginning
---

![someone is coding](/images/christin-hume-mfB1B1s4sMc-unsplash.jpg)

Flask is a micro web framework written in Python and based on the Werkzeug toolkit and Jinja2 template engine. In this post, I’m going to use the stable version of Flask 0.12.2

[To install Flask in Ubuntu](https://flask.palletsprojects.com/en/3.0.x/installation/)

Let us understand the following lines:

```
1. from flask import Flask
2. app = Flask(__name__)
3. if __name__ == "__main__":
4.     app.run()
```

1. We import the flask dependency. Remember to use a capital Flask while importing.
2. We create the app object as an instance of class Flask imported from the flask package. The `__name__` variable passed to the `Flask` class is a Python predefined variable, which is set to the name of the module in which it is used. It is helpful when we want to find other static files such as HTML, CSS files.
3. `__name__ == "__main__"` is required for a quick check so as to make sure that we only start the web server or web app when this piece of code is called directly.
4. `app.run()` is used to run the code.
