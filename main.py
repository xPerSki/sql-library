from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)


with app.app_context():
    db.create_all()


@app.route('/', methods=["POST", "GET"])
def home():
    query = db.select(Book).order_by(Book.id)
    result = db.session.execute(query)
    all_books = result.scalars()
    return render_template("index.html", books=all_books)


@app.route("/add", methods=["POST", "GET"])
def add():
    if request.method == "POST":
        data = request.form
        new_book = Book(title=data['title'], author=data['author'], rating=data['rating'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("add.html")


@app.route("/edit id=<int:edit_id>", methods=["POST", "GET"])
def edit(edit_id):
    query = db.select(Book).where(Book.id == edit_id)
    result = db.session.execute(query)
    edit_book = result.scalar()

    if request.method == "POST":
        edit_book.rating = request.form['new_rating']
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", book=edit_book)


@app.route("/del<int:del_id>")
def delete(del_id):
    query = db.select(Book).where(Book.id == del_id)
    result = db.session.execute(query)
    del_book = result.scalar()
    db.session.delete(del_book)
    db.session.commit()
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
