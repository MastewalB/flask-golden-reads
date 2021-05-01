from application import app







""" @app.before_request
def make_session_permanent():
    session.permanent = True  """


def get_google_books_data(isbn):
    fallback = "https://images.unsplash.com/photo-1499482125586-91609c0b5fd4?ixid=MXwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHw%3D&ixlib=rb-1.2.1&auto=format&fit=crop&w=634&q=80"
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={isbn}&key=AIzaSyDTPZR0X5RS-Vb7k00pG9QfmykL-yTE514").json()
    items = response.get("items")
    rating = 0
    ratingsCount = 0
    pageNum = 0
    description = ""
    image_link = fallback

    if items:
        try:
            rating = items[0].get("volumeInfo").get("averageRating")
            ratingsCount = items[0].get("volumeInfo").get("ratingsCount")
            description = items[0].get("volumeInfo").get("description")
            pageNum = items[0].get("volumeInfo").get("pageCount")
            image_link = items[0].get("volumeInfo").get("imageLinks").get("thumbnail")
        except:
            rating = 0
            ratingsCount = 0
            pageNum = 0
            description = ""
            image_link = fallback
    
    return [pageNum, rating, description, image_link, ratingsCount]





get_google_books_data('1451648537')
if __name__ == '__main__':
    app.debug = True
    app.run()
