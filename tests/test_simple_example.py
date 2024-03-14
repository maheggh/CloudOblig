def remove_src(path_list):
    if path_list[-1].lower() == 'src':
        path_list = path_list[:-1]
    return path_list


def test_remove_src():
    path_list1 = ['path', 'to', 'src']
    path_list1 = remove_src(path_list1)
    assert path_list1 == ['path', 'to']

    path_list2 = ['path', 'to', 'source']
    path_list2 = remove_src(path_list2)
    assert path_list2 == ['path', 'to', 'source']

    path_list3 = ['path', 'to', 'srcsrc']
    path_list3 = remove_src(path_list3)
    assert path_list3 == ['path', 'to', 'srcsrc']

    path_list4 = ['path', 'to', 'src', 'code']
    path_list4 = remove_src(path_list4)
    assert path_list4 == ['path', 'to', 'src', 'code']

    path_list5 = ['path', 'to', 'SRC']
    path_list5 = remove_src(path_list5)
    assert path_list5 == ['path', 'to']
