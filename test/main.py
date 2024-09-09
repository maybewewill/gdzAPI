import asyncio
from gdzapi.gdzapi import AsyncGDZ

async def main():
    async with AsyncGDZ() as gdz:
        subjects = await gdz.subjects
        for class_ in subjects:
            if class_.name == "Биология":
                books = await gdz.get_books(class_)
                if books:
                    book = books[0]
                    print(book)
                pages = await gdz.get_pages("/class-10/himiya/gabrielyan-sladkov-bazovij/")
                print(pages)

                if pages:
                    solutions = await gdz.get_gdz(pages[0].url)
                    print(solutions)

if __name__ == "__main__":
    asyncio.run(main())
