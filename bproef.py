alreadydone= [(1,4,6)]

def product(ar_list):
    if not ar_list:
        yield ()
    else:
        for a in ar_list[0]:
            for prod in product(ar_list[1:]):
                yield (a,)+prod

print(list(product([[1,2],[3,4],[5,6]])))