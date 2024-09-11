from gdzapi import Euroki

e = Euroki()
books = e.search_books("Биология 10 класс")
for book in books:
    if "Каменский" in book.authors:
        downloadable_images = []
        for i in book.pages:
            for j in i.solutions:
                downloadable_images.append(j.image_src)
        print(downloadable_images)
