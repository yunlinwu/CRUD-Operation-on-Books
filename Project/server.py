# Initialize Flask App
from flask import Flask, render_template, request, redirect, url_for, jsonify
import re, uuid
from jinja2 import escape, Markup
# Dataset is stored in 'books.py'
from books import book_data as books

app = Flask(__name__) # Create the Flask app instance


# Defining App Routes

# Homepage Route
@app.route('/')
def home():
    # Including book IDs in the popular_books data passed to the template
    popular_books = [{**books[book_id], 'ID': book_id} for book_id in list(books)[:3]]  # Get the first 3 books with their IDs
    return render_template('index.html', popular_books=popular_books)

# Search Route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').lower().strip()
    matching_books = []
    if query:
        for id, book in books.items():
            if query in book['Title'].lower() or query in book['Author'].lower() or query in book['Genre'].lower():
                # Create a copy of the book dictionary and add the ID
                book_with_id = book.copy()
                book_with_id['ID'] = id
                matching_books.append(book_with_id)

    return render_template('search.html', query=query, results=matching_books)


# View Route
@app.route('/view/<id>')
def view(id):
    book = books.get(id)
    if not book:
        return "Book not found", 404

    # Extract numeric part of the rating and convert to float
    rating_value = float(book['Rating'].split()[0])  # Split the string and take the first part
    filled_stars = round(rating_value)  # Round to nearest whole number

    unfilled_stars = 5 - filled_stars

    # Fetch similar books' details
    similar_books = []
    for similar_id in book.get('Similar Books IDs', []):
        similar_book = books.get(similar_id)
        if similar_book:
            similar_books.append({'ID': similar_id, 'Title': similar_book['Title']})

    return render_template('view.html', book=book, id=id, similar_books=similar_books, filled_stars=filled_stars, unfilled_stars=unfilled_stars)
# Add Route
@app.route('/add', methods=['GET', 'POST'])
def add_book():
    if request.method == 'POST':
        try:
            # Extract and validate form data
            title = request.form.get('title', '').strip()
            author = request.form.get('author', '').strip()
            genre = request.form.get('genre', '').strip()
            year = request.form.get('year', '').strip()
            linkToCoverImage = request.form.get('linkToCoverImage', '').strip()
            summary = request.form.get('summary', '').strip()
            rating = request.form.get('rating', '').strip()
            tags = request.form.get('tags', '').strip().split(',')  # Assuming comma-separated
            similarBooksIDs = request.form.get('similarBooksIDs', '').strip().split(',')  # Assuming comma-separated

            # Basic validation (e.g., check if required fields are not empty)
            if not title or not author or not genre or not tags or not similarBooksIDs or not year.isdigit():
                raise ValueError("Missing or invalid data")

            rating = request.form.get('rating', '').strip()

            # Convert year to integer and validate
            year = int(request.form.get('year', '0'))
            if year <= 0:
                raise ValueError("Invalid year")

            # Validate rating
            rating_value = int(rating)  # This will raise ValueError if conversion fails
            if rating_value < 1 or rating_value > 5:
                raise ValueError("Rating must be an integer between 1 and 5")

            # Generate a unique ID for the new book
            new_id = str(uuid.uuid4())

            # Save the new book data
            books[new_id] = {
                "Title": title,
                "Author": author,
                "Genre": genre,
                "Year of Publication": int(year),
                "Link to Cover Image": linkToCoverImage,
                "Summary": summary,
                "Rating": rating,
                "Tags": tags,
                "Similar Books IDs": similarBooksIDs
            }

            return jsonify({"success": True, "message": "New item successfully created", "newItemId": new_id})
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400
    else:
        return render_template('add.html')

# Edit Route
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_book(id):
    book = books.get(id)
    if not book:
        return "Book not found", 404

    if request.method == 'POST':
        # Process the submitted form data and update the book
        book['Title'] = request.form['title']
        book['Author'] = request.form['author']
        book['Genre'] = request.form['genre']
        book['Year of Publication'] = request.form['year']
        book['Link to Cover Image'] = request.form['linkToCoverImage']
        book['Summary'] = request.form['summary']
        book['Rating'] = request.form['rating']
        book['Tags'] = request.form['tags'].split(',')
        book['Similar Books IDs'] = request.form['similarBooksIDs'].split(',')
        # Redirect to the view page to see the changes
        return redirect(url_for('view', id=id))
    else:
        # For GET request, show the edit form with current book data
        return render_template('edit.html', book=book, id=id)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
