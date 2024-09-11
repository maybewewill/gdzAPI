from gdzapi import MegaResheba

m = MegaResheba()
for s in m.subjects:
    if s.name == "История":
        try:
            print(s.books[0].pages[0].solutions[0].image_src)
        except:
            # This is means that there are no solutions
            print("No solutions")