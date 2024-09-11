import asyncio
from gdzapi import AsyncGDZ


async def main():
    async with AsyncGDZ() as gdz:
        subjects = await gdz.subjects
        for subject in subjects:
            if subject.name == "Биология":
                books = await subject.books
                if books:
                    book = books[0]
                    print(f"Book: {book.name}")

                pages = await book.pages
                if pages:
                    solutions = await pages[0].solutions
                    print(solutions[0].image_src)


if __name__ == "__main__":
    asyncio.run(main())