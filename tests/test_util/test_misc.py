#!/usr/bin/env python

"""Unit tests for utility functions and classes.
"""
from copy import copy, deepcopy
from os import remove, rmdir
from os.path import exists
from cogent3.util.unit_test import TestCase, main
from cogent3.util.misc import (iterable,
                               flatten, is_iterable, is_char, is_char_or_noniterable,
                               is_str_or_noniterable, not_list_tuple, list_flatten,
                               recursive_flatten, unflatten, select, find_all,
                               add_lowercase, InverseDict, InverseDictMulti, DictFromPos, DictFromFirst,
                               DictFromLast, DistanceFromMatrix, PairsFromGroups,
                               ClassChecker, Delegator, FunctionWrapper,
                               ConstraintError, ConstrainedContainer,
                               ConstrainedString, ConstrainedList, ConstrainedDict,
                               MappedString, MappedList, MappedDict,
                               NonnegIntError, reverse_complement, not_none,
                               NestedSplitter, curry, remove_files, get_random_directory_name,
                               create_dir, handle_error_codes, identity, if_,
                               to_string,
                               timeLimitReached, get_independent_coords, get_merged_by_value_coords,
                               get_merged_overlapping_coords, get_run_start_indices, get_tmp_filename,
                               get_format_suffixes)
from numpy import array
from time import clock, sleep

__author__ = "Rob Knight"
__copyright__ = "Copyright 2007-2016, The Cogent Project"
__credits__ = ["Rob Knight", "Amanda Birmingham", "Sandra Smit",
               "Zongzhi Liu", "Peter Maxwell", "Daniel McDonald"]
__license__ = "GPL"
__version__ = "3.0a2"
__maintainer__ = "Rob Knight"
__email__ = "rob@spot.colorado.edu"
__status__ = "Production"


class UtilsTests(TestCase):
    """Tests of individual functions in utils"""

    def setUp(self):
        """ """
        self.files_to_remove = []
        self.dirs_to_remove = []

    def tearDown(self):
        """ """
        list(map(remove, self.files_to_remove))
        list(map(rmdir, self.dirs_to_remove))

    def test_identity(self):
        """should return same object"""
        foo = [1, 'a', lambda x: x]
        exp = id(foo)
        self.assertEqual(id(identity(foo)), exp)

    def test_if_(self):
        """implementation of c-like tertiary operator"""
        exp = 'yay'
        obs = if_(True, 'yay', 'nay')
        self.assertEqual(obs, exp)
        exp = 'nay'
        obs = if_(False, 'yay', 'nay')
        self.assertEqual(obs, exp)

    def test_to_string(self):
        """should stringify an object"""
        class foo(object):

            def __init__(self):
                self.bar = 5
        exp = 'bar: 5'
        obs = to_string(foo())
        self.assertEqual(obs, exp)

    # this test and the code it tests is architecture dependent. that is not
    # good.
    # def test_timeLimitReached(self):
    #    """should return true if timelimit has been reached, else return false"""
    #    start = clock()
    #    timelimit = .0002
    #    exp = False
    #    sleep(1)
    #    obs = timeLimitReached(start, timelimit)
    #    self.assertEqual(obs, exp)
    #    sleep(1)
    #    exp = True
    #    obs = timeLimitReached(start, timelimit)
    #    self.assertEqual(obs, exp)

    def test_iterable(self):
        """iterable(x) should return x or [x], always an iterable result"""
        self.assertEqual(iterable('x'), 'x')
        self.assertEqual(iterable(''), '')
        self.assertEqual(iterable(3), [3])
        self.assertEqual(iterable(None), [None])
        self.assertEqual(iterable({'a': 1}), {'a': 1})
        self.assertEqual(iterable(['a', 'b', 'c']), ['a', 'b', 'c'])

    def test_flatten_no_change(self):
        """flatten should not change non-nested sequences (except to list)"""
        self.assertEqual(flatten('abcdef'), list('abcdef'))  # test identities
        self.assertEqual(flatten([]), [])  # test empty sequence
        self.assertEqual(flatten(''), [])  # test empty string

    def test_flatten(self):
        """flatten should remove one level of nesting from nested sequences"""
        self.assertEqual(flatten(['aa', 'bb', 'cc']), list('aabbcc'))
        self.assertEqual(flatten([1, [2, 3], [[4, [5]]]]), [1, 2, 3, [4, [5]]])

    def test_is_iterable(self):
        """is_iterable should return True for iterables"""
        # test str
        self.assertEqual(is_iterable('aa'), True)
        # test list
        self.assertEqual(is_iterable([3, 'aa']), True)
        # test Number, expect False
        self.assertEqual(is_iterable(3), False)

    def test_is_char(self):
        """is_char(obj) should return True when obj is a char"""
        self.assertEqual(is_char('a'), True)
        self.assertEqual(is_char('ab'), False)
        self.assertEqual(is_char(''), True)
        self.assertEqual(is_char([3]), False)
        self.assertEqual(is_char(3), False)

    def test_is_char_or_noniterable(self):
        """is_char_or_noniterable should return True or False"""
        self.assertEqual(is_char_or_noniterable('a'), True)
        self.assertEqual(is_char_or_noniterable('ab'), False)
        self.assertEqual(is_char_or_noniterable(3), True)
        self.assertEqual(is_char_or_noniterable([3]), False)

    def test_is_str_or_noniterable(self):
        """is_str_or_noniterable should return True or False"""
        self.assertEqual(is_str_or_noniterable('a'), True)
        self.assertEqual(is_str_or_noniterable('ab'), True)
        self.assertEqual(is_str_or_noniterable(3), True)
        self.assertEqual(is_str_or_noniterable([3]), False)

    def test_recursive_flatten(self):
        """recursive_flatten should remove all nesting from nested sequences"""
        self.assertEqual(recursive_flatten(
            [1, [2, 3], [[4, [5]]]]), [1, 2, 3, 4, 5])

        # test default behavior on str unpacking
        self.assertEqual(recursive_flatten(
            ['aa', [8, 'cc', 'dd'], ['ee', ['ff', 'gg']]]),
            ['a', 'a', 8, 'c', 'c', 'd', 'd', 'e', 'e', 'f', 'f', 'g', 'g'])

        # test str untouched flattening using is_leaf=is_str_or_noniterable
        self.assertEqual(recursive_flatten(
            ['aa', [8, 'cc', 'dd'], ['ee', ['ff', 'gg']]],
            is_leaf=is_str_or_noniterable),
            ['aa', 8, 'cc', 'dd', 'ee', 'ff', 'gg'])

    def test_create_dir(self):
        """create_dir creates dir and fails meaningful."""

        tmp_dir_path = get_random_directory_name()
        tmp_dir_path2 = get_random_directory_name(suppress_mkdir=True)
        tmp_dir_path3 = get_random_directory_name(suppress_mkdir=True)

        self.dirs_to_remove.append(tmp_dir_path)
        self.dirs_to_remove.append(tmp_dir_path2)
        self.dirs_to_remove.append(tmp_dir_path3)

        # create on existing dir raises OSError if fail_on_exist=True
        self.assertRaises(OSError, create_dir, tmp_dir_path,
                          fail_on_exist=True)
        self.assertEqual(create_dir(tmp_dir_path,
                                    fail_on_exist=True,
                                    handle_errors_externally=True), 1)

        # return should be 1 if dir exist and fail_on_exist=False
        self.assertEqual(create_dir(tmp_dir_path, fail_on_exist=False), 1)

        # if dir not there make it and return always 0
        self.assertEqual(create_dir(tmp_dir_path2), 0)
        self.assertEqual(create_dir(tmp_dir_path3, fail_on_exist=True), 0)

    def test_handle_error_codes(self):
        """handle_error_codes raises the right error."""

        self.assertRaises(OSError, handle_error_codes, "test", False, 1)
        self.assertEqual(handle_error_codes("test", True, 1), 1)
        self.assertEqual(handle_error_codes("test", False, 0), 0)
        self.assertEqual(handle_error_codes("test"), 0)

    def test_not_list_tuple(self):
        """not_list_tuple(obj) should return False when obj is list or tuple"""
        self.assertEqual(not_list_tuple([8, 3]), False)
        self.assertEqual(not_list_tuple((8, 3)), False)
        self.assertEqual(not_list_tuple('34'), True)

    def test_list_flatten(self):
        """list_flatten should remove all nesting, str is untouched """
        self.assertEqual(list_flatten(
            ['aa', [8, 'cc', 'dd'], ['ee', ['ff', 'gg']]], ),
            ['aa', 8, 'cc', 'dd', 'ee', 'ff', 'gg'])

    def test_recursive_flatten_max_depth(self):
        """recursive_flatten should not remover more than max_depth levels"""
        self.assertEqual(recursive_flatten(
            [1, [2, 3], [[4, [5]]]]), [1, 2, 3, 4, 5])
        self.assertEqual(recursive_flatten([1, [2, 3], [[4, [5]]]], 0),
                         [1, [2, 3], [[4, [5]]]])
        self.assertEqual(recursive_flatten([1, [2, 3], [[4, [5]]]], 1),
                         [1, 2, 3, [4, [5]]])
        self.assertEqual(recursive_flatten([1, [2, 3], [[4, [5]]]], 2),
                         [1, 2, 3, 4, [5]])
        self.assertEqual(recursive_flatten([1, [2, 3], [[4, [5]]]], 3),
                         [1, 2, 3, 4, 5])
        self.assertEqual(recursive_flatten([1, [2, 3], [[4, [5]]]], 5000),
                         [1, 2, 3, 4, 5])

    def test_unflatten(self):
        """unflatten should turn a 1D sequence into a 2D list"""
        self.assertEqual(unflatten("abcdef", 1), list("abcdef"))
        self.assertEqual(unflatten("abcdef", 1, True), list("abcdef"))
        self.assertEqual(unflatten("abcdef", 2), ['ab', 'cd', 'ef'])
        self.assertEqual(unflatten("abcdef", 3), ['abc', 'def'])
        self.assertEqual(unflatten("abcdef", 4), ['abcd'])
        # should be able to preserve extra items
        self.assertEqual(unflatten("abcdef", 4, True), ['abcd', 'ef'])
        self.assertEqual(unflatten("abcdef", 10), [])
        self.assertEqual(unflatten("abcdef", 10, True), ['abcdef'])
        # should succeed on empty sequnce
        self.assertEqual(unflatten('', 10), [])

    def test_unflatten_bad_row_width(self):
        "unflatten should raise ValueError with row_width < 1"""
        self.assertRaises(ValueError, unflatten, "abcd", 0)
        self.assertRaises(ValueError, unflatten, "abcd", -1)

    def test_select_sequence(self):
        """select should work on a sequence with a list of indices"""
        chars = 'abcdefghij'
        strings = list(chars)

        tests = {(0,): ['a'],
                 (-1,): ['j'],
                 (0, 2, 4): ['a', 'c', 'e'],
                 (9, 8, 7, 6, 5, 4, 3, 2, 1, 0): list('jihgfedcba'),
                 (-8, 8): ['c', 'i'],
                 (): [],
                 }
        for test, result in list(tests.items()):
            self.assertEqual(select(test, chars), result)
            self.assertEqual(select(test, strings), result)

    def test_select_empty(self):
        """select should raise error if indexing into empty sequence"""
        self.assertRaises(IndexError, select, [1], [])

    def test_select_mapping(self):
        """select should return the values corresponding to a list of keys"""
        values = {'a': 5, 'b': 2, 'c': 4, 'd': 6, 'e': 7}
        self.assertEqual(select('abc', values), [5, 2, 4])
        self.assertEqual(select(['e', 'e', 'e'], values), [7, 7, 7])
        self.assertEqual(select(('e', 'b', 'a'), values), [7, 2, 5])
        # check that it raises KeyError on anything out of range
        self.assertRaises(KeyError, select, 'abx', values)

    def test_find_all(self):
        """find_all should return list of all occurrences"""
        self.assertEqual(find_all('abc', 'd'), [])
        self.assertEqual(find_all('abc', 'a'), [0])
        self.assertEqual(find_all('abcabca', 'a'), [0, 3, 6])
        self.assertEqual(find_all('abcabca', 'c'), [2, 5])
        self.assertEqual(find_all('abcabca', '3'), [])
        self.assertEqual(find_all('abcabca', 'bc'), [1, 4])
        self.assertRaises(TypeError, find_all, 'abcabca', 3)

    def test_add_lowercase(self):
        """add_lowercase should add lowercase version of each key w/ same val"""
        d = {'a': 1, 'b': 'test', 'A': 5, 'C': 123, 'D': [], 'AbC': 'XyZ',
             None: '3', '$': 'abc', 145: '5'}
        add_lowercase(d)
        assert d['d'] is d['D']
        d['D'].append(3)
        self.assertEqual(d['D'], [3])
        self.assertEqual(d['d'], [3])
        self.assertNotEqual(d['a'], d['A'])
        self.assertEqual(d, {'a': 1, 'b': 'test', 'A': 5, 'C': 123, 'c': 123,
                             'D': [3], 'd': [3], 'AbC': 'XyZ', 'abc': 'xyz', None: '3', '$': 'abc',
                             145: '5'})

        # should work with strings
        d = 'ABC'
        self.assertEqual(add_lowercase(d), 'ABCabc')
        # should work with tuples
        d = tuple('ABC')
        self.assertEqual(add_lowercase(d), tuple('ABCabc'))
        # should work with lists
        d = list('ABC')
        self.assertEqual(add_lowercase(d), list('ABCabc'))
        # should work with sets
        d = set('ABC')
        self.assertEqual(add_lowercase(d), set('ABCabc'))
        # ...even frozensets
        d = frozenset('ABC')
        self.assertEqual(add_lowercase(d), frozenset('ABCabc'))

    def test_add_lowercase_tuple(self):
        """add_lowercase should deal with tuples correctly"""
        d = {('A', 'B'): 'C', ('D', 'e'): 'F', ('b', 'c'): 'H'}
        add_lowercase(d)
        self.assertEqual(d, {
            ('A', 'B'): 'C',
            ('a', 'b'): 'c',
            ('D', 'e'): 'F',
            ('d', 'e'): 'f',
            ('b', 'c'): 'H',
        })

    def test_InverseDict(self):
        """InverseDict should invert dict's keys and values"""
        self.assertEqual(InverseDict({}), {})
        self.assertEqual(InverseDict({'3': 4}), {4: '3'})
        self.assertEqual(InverseDict({'a': 'x', 'b': 1, 'c': None, 'd': ('a', 'b')}),
                         {'x': 'a', 1: 'b', None: 'c', ('a', 'b'): 'd'})
        self.assertRaises(TypeError, InverseDict, {'a': ['a', 'b', 'c']})
        d = InverseDict({'a': 3, 'b': 3, 'c': 3})
        self.assertEqual(len(d), 1)
        assert 3 in d
        assert d[3] in 'abc'

    def test_InverseDictMulti(self):
        """InverseDictMulti should invert keys and values, keeping all keys"""
        self.assertEqual(InverseDictMulti({}), {})
        self.assertEqual(InverseDictMulti({'3': 4}), {4: ['3']})
        self.assertEqual(InverseDictMulti(
            {'a': 'x', 'b': 1, 'c': None, 'd': ('a', 'b')}),
            {'x': ['a'], 1: ['b'], None: ['c'], ('a', 'b'): ['d']})
        self.assertRaises(TypeError, InverseDictMulti, {'a': ['a', 'b', 'c']})
        d = InverseDictMulti({'a': 3, 'b': 3, 'c': 3, 'd': '3', 'e': '3'})
        self.assertEqual(len(d), 2)
        assert 3 in d
        d3_items = d[3][:]
        self.assertEqual(len(d3_items), 3)
        d3_items.sort()
        self.assertEqual(''.join(d3_items), 'abc')
        assert '3' in d
        d3_items = d['3'][:]
        self.assertEqual(len(d3_items), 2)
        d3_items.sort()
        self.assertEqual(''.join(d3_items), 'de')

    def test_DictFromPos(self):
        """DictFromPos should return correct lists of positions"""
        d = DictFromPos
        self.assertEqual(d(''), {})
        self.assertEqual(d('a'), {'a': [0]})
        self.assertEqual(d(['a', 'a', 'a']), {'a': [0, 1, 2]})
        self.assertEqual(d('abacdeeee'), {'a': [0, 2], 'b': [1], 'c': [3], 'd': [4],
                                          'e': [5, 6, 7, 8]})
        self.assertEqual(d(('abc', None, 'xyz', None, 3)), {'abc': [0], None: [1, 3],
                                                            'xyz': [2], 3: [4]})

    def test_DictFromFirst(self):
        """DictFromFirst should return correct first positions"""
        d = DictFromFirst
        self.assertEqual(d(''), {})
        self.assertEqual(d('a'), {'a': 0})
        self.assertEqual(d(['a', 'a', 'a']), {'a': 0})
        self.assertEqual(d('abacdeeee'), {
                         'a': 0, 'b': 1, 'c': 3, 'd': 4, 'e': 5})
        self.assertEqual(d(('abc', None, 'xyz', None, 3)), {'abc': 0, None: 1,
                                                            'xyz': 2, 3: 4})

    def test_DictFromLast(self):
        """DictFromLast should return correct last positions"""
        d = DictFromLast
        self.assertEqual(d(''), {})
        self.assertEqual(d('a'), {'a': 0})
        self.assertEqual(d(['a', 'a', 'a']), {'a': 2})
        self.assertEqual(d('abacdeeee'), {
                         'a': 2, 'b': 1, 'c': 3, 'd': 4, 'e': 8})
        self.assertEqual(d(('abc', None, 'xyz', None, 3)), {'abc': 0, None: 3,
                                                            'xyz': 2, 3: 4})

    def test_DistanceFromMatrix(self):
        """DistanceFromMatrix should return correct elements"""
        m = {'a': {'3': 4, 6: 1}, 'b': {'3': 5, '6': 2}}
        d = DistanceFromMatrix(m)
        self.assertEqual(d('a', '3'), 4)
        self.assertEqual(d('a', 6), 1)
        self.assertEqual(d('b', '3'), 5)
        self.assertEqual(d('b', '6'), 2)
        self.assertRaises(KeyError, d, 'c', 1)
        self.assertRaises(KeyError, d, 'b', 3)

    def test_PairsFromGroups(self):
        """PairsFromGroups should return dict with correct pairs"""
        empty = []
        self.assertEqual(PairsFromGroups(empty), {})
        one = ['abc']
        self.assertEqual(PairsFromGroups(one), dict.fromkeys([
            ('a', 'a'), ('a', 'b'), ('a', 'c'),
            ('b', 'a'), ('b', 'b'), ('b', 'c'),
            ('c', 'a'), ('c', 'b'), ('c', 'c'),
        ]))

        two = ['xy', 'abc']
        self.assertEqual(PairsFromGroups(two), dict.fromkeys([
            ('a', 'a'), ('a', 'b'), ('a', 'c'),
            ('b', 'a'), ('b', 'b'), ('b', 'c'),
            ('c', 'a'), ('c', 'b'), ('c', 'c'),
            ('x', 'x'), ('x', 'y'), ('y', 'x'), ('y', 'y'),
        ]))
        # if there's overlap, note that the groups should _not_ be expanded
        # (e.g. in the following case, 'x' is _not_ similar to 'c', even though
        # both 'x' and 'c' are similar to 'a'.
        overlap = ['ax', 'abc']
        self.assertEqual(PairsFromGroups(overlap), dict.fromkeys([
            ('a', 'a'), ('a', 'b'), ('a', 'c'),
            ('b', 'a'), ('b', 'b'), ('b', 'c'),
            ('c', 'a'), ('c', 'b'), ('c', 'c'),
            ('x', 'x'), ('x', 'a'), ('a', 'x'),
        ]))

    def test_remove_files(self):
        """Remove files functions as expected """
        # create list of temp file paths
        test_filepaths = \
            [get_tmp_filename(prefix='remove_files_test') for i in range(5)]

        # try to remove them with remove_files and verify that an IOError is
        # raises
        self.assertRaises(OSError, remove_files, test_filepaths)
        # now get no error when error_on_missing=False
        remove_files(test_filepaths, error_on_missing=False)

        # touch one of the filepaths so it exists
        open(test_filepaths[2], 'w').close()
        # check that an error is raised on trying to remove the files...
        self.assertRaises(OSError, remove_files, test_filepaths)
        # ... but that the existing file was still removed
        self.assertFalse(exists(test_filepaths[2]))

        # touch one of the filepaths so it exists
        open(test_filepaths[2], 'w').close()
        # no error is raised on trying to remove the files
        # (although 4 don't exist)...
        remove_files(test_filepaths, error_on_missing=False)
        # ... and the existing file was removed
        self.assertFalse(exists(test_filepaths[2]))

    def test_get_random_directory_name(self):
        """get_random_directory_name functions as expected """
        # repeated calls yield different directory names
        dirs = []
        for i in range(100):
            d = get_random_directory_name(suppress_mkdir=True)
            self.assertTrue(d not in dirs)
            dirs.append(d)

        actual = get_random_directory_name(suppress_mkdir=True)
        self.assertFalse(exists(actual), 'Random dir exists: %s' % actual)
        self.assertTrue(actual.startswith('/'),
                        'Random dir is not a full path: %s' % actual)

        # prefix, suffix and output_dir are used as expected
        actual = get_random_directory_name(suppress_mkdir=True, prefix='blah',
                                           output_dir='/tmp/', suffix='stuff')
        self.assertTrue(actual.startswith('/tmp/blah2'),
                        'Random dir does not begin with output_dir + prefix ' +
                        '+ 2 (where 2 indicates the millenium in the timestamp): %s' % actual)
        self.assertTrue(actual.endswith('stuff'),
                        'Random dir does not end with suffix: %s' % actual)

        # changing rand_length functions as expected
        actual1 = get_random_directory_name(suppress_mkdir=True)
        actual2 = get_random_directory_name(suppress_mkdir=True,
                                            rand_length=10)
        actual3 = get_random_directory_name(suppress_mkdir=True,
                                            rand_length=0)
        self.assertTrue(len(actual1) > len(actual2) > len(actual3),
                        "rand_length does not affect directory name lengths " +
                        "as expected:\n%s\n%s\n%s" % (actual1, actual2, actual3))

        # changing the timestamp pattern functions as expected
        actual1 = get_random_directory_name(suppress_mkdir=True)
        actual2 = get_random_directory_name(suppress_mkdir=True,
                                            timestamp_pattern='%Y')
        self.assertNotEqual(actual1, actual2)
        self.assertTrue(len(actual1) > len(actual2),
                        'Changing timestamp_pattern does not affect directory name')
        # empty string as timestamp works
        actual3 = get_random_directory_name(suppress_mkdir=True,
                                            timestamp_pattern='')
        self.assertTrue(len(actual2) > len(actual3))

        # creating the directory works as expected
        actual = get_random_directory_name(output_dir='/tmp/',
                                           prefix='get_random_directory_test')
        self.assertTrue(exists(actual))
        rmdir(actual)

    def test_independent_spans(self):
        """get_independent_coords returns truly non-overlapping (decorated) spans"""
        # single span is returned
        data = [(0, 20, 'a')]
        got = get_independent_coords(data)
        self.assertEqual(got, data)

        # multiple non-overlapping
        data = [(20, 30, 'a'), (35, 40, 'b'), (65, 75, 'c')]
        got = get_independent_coords(data)
        self.assertEqual(got, data)

        # over-lapping first/second returns first occurrence by default
        data = [(20, 30, 'a'), (25, 40, 'b'), (65, 75, 'c')]
        got = get_independent_coords(data)
        self.assertEqual(got, [(20, 30, 'a'), (65, 75, 'c')])
        # but randomly the first or second if random_tie_breaker is chosen
        got = get_independent_coords(data, random_tie_breaker=True)
        self.assertTrue(got in ([(20, 30, 'a'), (65, 75, 'c')],
                                [(25, 40, 'b'), (65, 75, 'c')]))

        # over-lapping second/last returns first occurrence by default
        data = [(20, 30, 'a'), (30, 60, 'b'), (50, 75, 'c')]
        got = get_independent_coords(data)
        self.assertEqual(got, [(20, 30, 'a'), (30, 60, 'b')])
        # but randomly the first or second if random_tie_breaker is chosen
        got = get_independent_coords(data, random_tie_breaker=True)
        self.assertTrue(got in ([(20, 30, 'a'), (50, 75, 'c')],
                                [(20, 30, 'a'), (30, 60, 'b')]))

        # over-lapping middle returns first occurrence by default
        data = [(20, 24, 'a'), (25, 40, 'b'), (30, 35, 'c'), (65, 75, 'd')]
        got = get_independent_coords(data)
        self.assertEqual(got, [(20, 24, 'a'), (25, 40, 'b'), (65, 75, 'd')])

        # but randomly the first or second if random_tie_breaker is chosen
        got = get_independent_coords(data, random_tie_breaker=True)
        self.assertTrue(got in ([(20, 24, 'a'), (25, 40, 'b'), (65, 75, 'd')],
                                [(20, 24, 'a'), (30, 35, 'c'), (65, 75, 'd')]))

    def test_get_merged_spans(self):
        """tests merger of overlapping spans"""
        sample = [[0, 10], [12, 15], [13, 16], [18, 25], [19, 20]]
        result = get_merged_overlapping_coords(sample)
        expect = [[0, 10], [12, 16], [18, 25]]
        self.assertEqual(result, expect)
        sample = [[0, 10], [5, 9], [12, 16], [18, 20], [19, 25]]
        result = get_merged_overlapping_coords(sample)
        expect = [[0, 10], [12, 16], [18, 25]]
        self.assertEqual(result, expect)

    def test_get_run_start_indices(self):
        """return indices corresponding to start of a run of identical values"""
        #       0  1  2  3  4  5  6  7
        data = [1, 2, 3, 3, 3, 4, 4, 5]
        expect = [[0, 1], [1, 2], [2, 3], [5, 4], [7, 5]]
        got = get_run_start_indices(data)
        self.assertEqual(list(got), expect)

        # raise an exception if try and provide a converter and num digits
        def wrap_gen():  # need to wrap generator so we can actually test this
            gen = get_run_start_indices(data, digits=1,
                                        converter_func=lambda x: x)

            def call():
                for v in gen:
                    pass
            return call

        self.assertRaises(AssertionError, wrap_gen())

    def test_merged_by_value_spans(self):
        """correctly merge adjacent spans with the same value"""
        # initial values same
        data = [[20, 21, 0], [21, 22, 0], [22, 23, 1], [23, 24, 0]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 22, 0], [22, 23, 1], [23, 24, 0]])

        # middle values same
        data = [[20, 21, 0], [21, 22, 1], [22, 23, 1], [23, 24, 0]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 21, 0], [21, 23, 1], [23, 24, 0]])

        # last values same
        data = [[20, 21, 0], [21, 22, 1], [22, 23, 0], [23, 24, 0]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 21, 0], [21, 22, 1], [22, 24, 0]])

        # all unique values
        data = [[20, 21, 0], [21, 22, 1], [22, 23, 2], [23, 24, 0]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 21, 0], [21, 22, 1], [22, 23, 2], [23, 24, 0]])

        # all values same
        data = [[20, 21, 0], [21, 22, 0], [22, 23, 0], [23, 24, 0]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 24, 0]])

        # all unique values to 2nd decimal
        data = [[20, 21, 0.11], [21, 22, 0.12], [22, 23, 0.13], [23, 24, 0.14]]
        self.assertEqual(get_merged_by_value_coords(data),
                         [[20, 21, 0.11], [21, 22, 0.12], [22, 23, 0.13], [23, 24, 0.14]])

        # all values same at 1st decimal
        data = [[20, 21, 0.11], [21, 22, 0.12], [22, 23, 0.13], [23, 24, 0.14]]
        self.assertEqual(get_merged_by_value_coords(data, digits=1),
                         [[20, 24, 0.1]])

    def test_get_format_suffixes(self):
        """correctly return suffixes for compressed etc.. formats"""
        a, b = get_format_suffixes("no_suffixes")
        self.assertTrue(a == b == None)
        a, b = get_format_suffixes("suffixes.gz")
        self.assertTrue(a == None and b == "gz")
        a, b = get_format_suffixes("suffixes.abcd")
        self.assertTrue(a == "abcd" and b == None)
        a, b = get_format_suffixes("suffixes.abcd.bz2")
        self.assertTrue(a == "abcd" and b == "bz2")


class _my_dict(dict):
    """Used for testing subclass behavior of ClassChecker"""
    pass


class ClassCheckerTests(TestCase):
    """Unit tests for the ClassChecker class."""

    def setUp(self):
        """define a few standard checkers"""
        self.strcheck = ClassChecker(str)
        self.intcheck = ClassChecker(int, int)
        self.numcheck = ClassChecker(float, int, int)
        self.emptycheck = ClassChecker()
        self.dictcheck = ClassChecker(dict)
        self.mydictcheck = ClassChecker(_my_dict)

    def test_init_good(self):
        """ClassChecker should init OK when initialized with classes"""
        self.assertEqual(self.strcheck.Classes, [str])
        self.assertEqual(self.numcheck.Classes, [float, int, int])
        self.assertEqual(self.emptycheck.Classes, [])

    def test_init_bad(self):
        """ClassChecker should raise TypeError if initialized with non-class"""
        self.assertRaises(TypeError, ClassChecker, 'x')
        self.assertRaises(TypeError, ClassChecker, str, None)

    def test_contains(self):
        """ClassChecker should return True only if given instance of class"""
        self.assertEqual(self.strcheck.__contains__('3'), True)
        self.assertEqual(self.strcheck.__contains__('ahsdahisad'), True)
        self.assertEqual(self.strcheck.__contains__(3), False)
        self.assertEqual(self.strcheck.__contains__({3: 'c'}), False)

        self.assertEqual(self.intcheck.__contains__('ahsdahisad'), False)
        self.assertEqual(self.intcheck.__contains__('3'), False)
        self.assertEqual(self.intcheck.__contains__(3.0), False)
        self.assertEqual(self.intcheck.__contains__(3), True)
        self.assertEqual(self.intcheck.__contains__(4**60), True)
        self.assertEqual(self.intcheck.__contains__(4**60 * -1), True)

        d = _my_dict()
        self.assertEqual(self.dictcheck.__contains__(d), True)
        self.assertEqual(self.dictcheck.__contains__({'d': 1}), True)
        self.assertEqual(self.mydictcheck.__contains__(d), True)
        self.assertEqual(self.mydictcheck.__contains__({'d': 1}), False)

        self.assertEqual(self.emptycheck.__contains__('d'), False)

        self.assertEqual(self.numcheck.__contains__(3), True)
        self.assertEqual(self.numcheck.__contains__(3.0), True)
        self.assertEqual(self.numcheck.__contains__(-3), True)
        self.assertEqual(self.numcheck.__contains__(-3.0), True)
        self.assertEqual(self.numcheck.__contains__(3e-300), True)
        self.assertEqual(self.numcheck.__contains__(0), True)
        self.assertEqual(self.numcheck.__contains__(4**1000), True)
        self.assertEqual(self.numcheck.__contains__('4**1000'), False)

    def test_str(self):
        """ClassChecker str should be the same as str(self.Classes)"""
        for c in [self.strcheck, self.intcheck, self.numcheck, self.emptycheck,
                  self.dictcheck, self.mydictcheck]:
            self.assertEqual(str(c), str(c.Classes))

    def test_copy(self):
        """copy.copy should work correctly on ClassChecker"""
        c = copy(self.strcheck)
        assert c is not self.strcheck
        assert '3' in c
        assert 3 not in c
        assert c.Classes is self.strcheck.Classes

    def test_deepcopy(self):
        """copy.deepcopy should work correctly on ClassChecker"""
        c = deepcopy(self.strcheck)
        assert c is not self.strcheck
        assert '3' in c
        assert 3 not in c
        assert c.Classes is not self.strcheck.Classes


class modifiable_string(str):
    """Mutable class to allow arbitrary attributes to be set"""
    pass


class _list_and_string(list, Delegator):
    """Trivial class to demonstrate Delegator.
    """

    def __init__(self, items, string):
        Delegator.__init__(self, string)
        self.NormalAttribute = 'default'
        self._x = None
        self._constant = 'c'
        for i in items:
            self.append(i)

    def _get_rand_property(self):
        return self._x

    def _set_rand_property(self, value):
        self._x = value
    prop = property(_get_rand_property, _set_rand_property)

    def _get_constant_property(self):
        return self._constant
    constant = property(_get_constant_property)


class DelegatorTests(TestCase):
    """Verify that Delegator works with attributes and properties."""

    def test_init(self):
        """Delegator should init OK when data supplied"""
        ls = _list_and_string([1, 2, 3], 'abc')
        self.assertRaises(TypeError, _list_and_string, [123])

    def test_getattr(self):
        """Delegator should find attributes in correct places"""
        ls = _list_and_string([1, 2, 3], 'abcd')
        # behavior as list
        self.assertEqual(len(ls), 3)
        self.assertEqual(ls[0], 1)
        ls.reverse()
        self.assertEqual(ls, [3, 2, 1])
        # behavior as string
        self.assertEqual(ls.upper(), 'ABCD')
        self.assertEqual(len(ls.upper()), 4)
        self.assertEqual(ls.replace('a', 'x'), 'xbcd')
        # behavior of normal attributes
        self.assertEqual(ls.NormalAttribute, 'default')
        # behavior of properties
        self.assertEqual(ls.prop, None)
        self.assertEqual(ls.constant, 'c')
        # shouldn't be allowed to get unknown properties
        self.assertRaises(AttributeError, getattr, ls, 'xyz')
        # if the unknown property can be set in the forwarder, do it there
        flex = modifiable_string('abcd')
        ls_flex = _list_and_string([1, 2, 3], flex)
        ls_flex.blah = 'zxc'
        self.assertEqual(ls_flex.blah, 'zxc')
        self.assertEqual(flex.blah, 'zxc')
        # should get AttributeError if changing a read-only property
        self.assertRaises(AttributeError, setattr, ls, 'constant', 'xyz')

    def test_setattr(self):
        """Delegator should set attributes in correct places"""
        ls = _list_and_string([1, 2, 3], 'abcd')
        # ability to create a new attribute
        ls.xyz = 3
        self.assertEqual(ls.xyz, 3)
        # modify a normal attribute
        ls.NormalAttribute = 'changed'
        self.assertEqual(ls.NormalAttribute, 'changed')
        # modify a read/write property
        ls.prop = 'xyz'
        self.assertEqual(ls.prop, 'xyz')

    def test_copy(self):
        """copy.copy should work correctly on Delegator"""
        l = ['a']
        d = Delegator(l)
        c = copy(d)
        assert c is not d
        assert c._handler is d._handler

    def test_deepcopy(self):
        """copy.deepcopy should work correctly on Delegator"""
        l = ['a']
        d = Delegator(l)
        c = deepcopy(d)
        assert c is not d
        assert c._handler is not d._handler
        assert c._handler == d._handler


class FunctionWrapperTests(TestCase):
    """Tests of the FunctionWrapper class"""

    def test_init(self):
        """FunctionWrapper should initialize with any callable"""
        f = FunctionWrapper(str)
        g = FunctionWrapper(id)
        h = FunctionWrapper(iterable)
        x = 3
        self.assertEqual(f(x), '3')
        self.assertEqual(g(x), id(x))
        self.assertEqual(h(x), [3])

    def test_copy(self):
        """copy should work for FunctionWrapper objects"""
        f = FunctionWrapper(str)
        c = copy(f)
        assert c is not f
        assert c.Function is f.Function

    # NOTE: deepcopy does not work for FunctionWrapper objects because you
    # can't copy a function.


class _simple_container(object):
    """example of a container to constrain"""

    def __init__(self, data):
        self._data = list(data)

    def __getitem__(self, item):
        return self._data.__getitem__(item)


class _constrained_simple_container(_simple_container, ConstrainedContainer):
    """constrained version of _simple_container"""

    def __init__(self, data):
        _simple_container.__init__(self, data)
        ConstrainedContainer.__init__(self, None)


class ConstrainedContainerTests(TestCase):
    """Tests of the generic ConstrainedContainer interface."""

    def setUp(self):
        """Make a couple of standard containers"""
        self.alphabet = _constrained_simple_container('abc')
        self.numbers = _constrained_simple_container([1, 2, 3])
        self.alphacontainer = 'abcdef'
        self.numbercontainer = ClassChecker(int)

    def test_matchesConstraint(self):
        """ConstrainedContainer matchesConstraint should return true if items ok"""
        self.assertEqual(self.alphabet.matches_constraint(self.alphacontainer),
                         True)
        self.assertEqual(self.alphabet.matches_constraint(self.numbercontainer),
                         False)
        self.assertEqual(self.numbers.matches_constraint(self.alphacontainer),
                         False)
        self.assertEqual(self.numbers.matches_constraint(self.numbercontainer),
                         True)

    def test_other_is_valid(self):
        """ConstrainedContainer should use constraint for checking other"""
        self.assertEqual(self.alphabet.other_is_valid('12d8jc'), True)
        self.alphabet.constraint = self.alphacontainer
        self.assertEqual(self.alphabet.other_is_valid('12d8jc'), False)
        self.alphabet.constraint = list('abcdefghijkl12345678')
        self.assertEqual(self.alphabet.other_is_valid('12d8jc'), True)
        self.assertEqual(self.alphabet.other_is_valid('z'), False)

    def test_item_is_valid(self):
        """ConstrainedContainer should use constraint for checking item"""
        self.assertEqual(self.alphabet.item_is_valid(3), True)
        self.alphabet.constraint = self.alphacontainer
        self.assertEqual(self.alphabet.item_is_valid(3), False)
        self.assertEqual(self.alphabet.item_is_valid('a'), True)

    def test_sequence_is_valid(self):
        """ConstrainedContainer should use constraint for checking sequence"""
        self.assertEqual(self.alphabet.sequence_is_valid('12d8jc'), True)
        self.alphabet.constraint = self.alphacontainer
        self.assertEqual(self.alphabet.sequence_is_valid('12d8jc'), False)
        self.alphabet.constraint = list('abcdefghijkl12345678')
        self.assertEqual(self.alphabet.sequence_is_valid('12d8jc'), True)
        self.assertEqual(self.alphabet.sequence_is_valid('z'), False)

    def test_Constraint(self):
        """ConstrainedContainer should only allow valid constraints to be set"""
        try:
            self.alphabet.constraint = self.numbers
        except ConstraintError:
            pass
        else:
            raise AssertionError(
                "Failed to raise ConstraintError with invalid constraint.")
        self.alphabet.constraint = 'abcdefghi'
        self.alphabet.constraint = ['a', 'b', 'c', 1, 2, 3]
        self.numbers.constraint = list(range(20))
        self.numbers.constraint = range(20)
        self.numbers.constraint = [5, 1, 3, 7, 2]
        self.numbers.constraint = {1: 'a', 2: 'b', 3: 'c'}
        self.assertRaises(ConstraintError, setattr, self.numbers,
                          'constraint', '1')


class ConstrainedStringTests(TestCase):
    """Tests that ConstrainedString can only contain allowed items."""

    def test_init_good_data(self):
        """ConstrainedString should init OK if string matches constraint"""
        self.assertEqual(ConstrainedString('abc', 'abcd'), 'abc')
        self.assertEqual(ConstrainedString('', 'abcd'), '')
        items = [1, 2, 3.2234, (['a'], ['b'],), 'xyz']
        # should accept anything str() does if no constraint is passed
        self.assertEqual(ConstrainedString(items), str(items))
        self.assertEqual(ConstrainedString(items, None), str(items))
        self.assertEqual(ConstrainedString('12345'), str(12345))
        self.assertEqual(ConstrainedString(12345, '1234567890'), str(12345))
        # check that list is formatted correctly and chars are all there
        test_list = [1, 2, 3, 4, 5]
        self.assertEqual(ConstrainedString(
            test_list, '][, 12345'), str(test_list))

    def test_init_bad_data(self):
        """ConstrainedString should fail init if unknown chars in string"""
        self.assertRaises(ConstraintError, ConstrainedString, 1234, '123')
        self.assertRaises(ConstraintError, ConstrainedString, '1234', '123')
        self.assertRaises(ConstraintError, ConstrainedString, [1, 2, 3], '123')

    def test_add_prevents_bad_data(self):
        """ConstrainedString should allow addition only of compliant string"""
        a = ConstrainedString('123', '12345')
        b = ConstrainedString('444', '4')
        c = ConstrainedString('45', '12345')
        d = ConstrainedString('x')
        self.assertEqual(a + b, '123444')
        self.assertEqual(a + c, '12345')
        self.assertRaises(ConstraintError, b.__add__, c)
        self.assertRaises(ConstraintError, c.__add__, d)
        # should be OK if constraint removed
        b.constraint = None
        self.assertEqual(b + c, '44445')
        self.assertEqual(b + d, '444x')
        # should fail if we add the constraint back
        b.constraint = '4x'
        self.assertEqual(b + d, '444x')
        self.assertRaises(ConstraintError, b.__add__, c)
        # check that added strings retain constraint
        self.assertRaises(ConstraintError, (a + b).__add__, d)

    def test_mul(self):
        """ConstrainedString mul amd rmul should retain constraint"""
        a = ConstrainedString('123', '12345')
        b = 3 * a
        c = b * 2
        self.assertEqual(b, '123123123')
        self.assertEqual(c, '123123123123123123')
        self.assertRaises(ConstraintError, b.__add__, 'x')
        self.assertRaises(ConstraintError, c.__add__, 'x')

    def test_getslice(self):
        """ConstrainedString getslice should remember constraint"""
        a = ConstrainedString('123333', '12345')
        b = a[2:4]
        self.assertEqual(b, '33')
        self.assertEqual(b.constraint, '12345')

    def test_getitem(self):
        """ConstrainedString getitem should handle slice objects"""
        a = ConstrainedString('7890543', '1234567890')
        self.assertEqual(a[0], '7')
        self.assertEqual(a[1], '8')
        self.assertEqual(a[-1], '3')
        self.assertRaises(AttributeError, getattr, a[1], 'alphabet')
        self.assertEqual(a[1:6:2], '804')
        self.assertEqual(a[1:6:2].constraint, '1234567890')

    def test_init_masks(self):
        """ConstrainedString should init OK with masks"""
        def mask(x):
            return str(int(x) + 3)
        a = ConstrainedString('12333', '45678', mask)
        self.assertEqual(a, '45666')
        assert 'x' not in a
        self.assertRaises(TypeError, a.__contains__, 1)


class MappedStringTests(TestCase):
    """MappedString should behave like ConstrainedString, but should map items."""

    def test_init_masks(self):
        """MappedString should init OK with masks"""
        def mask(x):
            return str(int(x) + 3)
        a = MappedString('12333', '45678', mask)
        self.assertEqual(a, '45666')
        assert 1 in a
        assert 'x' not in a


class ConstrainedListTests(TestCase):
    """Tests that bad data can't sneak into ConstrainedLists."""

    def test_init_good_data(self):
        """ConstrainedList should init OK if list matches constraint"""
        self.assertEqual(ConstrainedList('abc', 'abcd'), list('abc'))
        self.assertEqual(ConstrainedList('', 'abcd'), list(''))
        items = [1, 2, 3.2234, (['a'], ['b'],), list('xyz')]
        # should accept anything str() does if no constraint is passed
        self.assertEqual(ConstrainedList(items), items)
        self.assertEqual(ConstrainedList(items, None), items)
        self.assertEqual(ConstrainedList('12345'), list('12345'))
        # check that list is formatted correctly and chars are all there
        test_list = list('12345')
        self.assertEqual(ConstrainedList(test_list, '12345'), test_list)

    def test_init_bad_data(self):
        """ConstrainedList should fail init with items not in constraint"""
        self.assertRaises(ConstraintError, ConstrainedList, '1234', '123')
        self.assertRaises(ConstraintError, ConstrainedList,
                          [1, 2, 3], ['1', '2', '3'])

    def test_add_prevents_bad_data(self):
        """ConstrainedList should allow addition only of compliant data"""
        a = ConstrainedList('123', '12345')
        b = ConstrainedList('444', '4')
        c = ConstrainedList('45', '12345')
        d = ConstrainedList('x')
        self.assertEqual(a + b, list('123444'))
        self.assertEqual(a + c, list('12345'))
        self.assertRaises(ConstraintError, b.__add__, c)
        self.assertRaises(ConstraintError, c.__add__, d)
        # should be OK if constraint removed
        b.constraint = None
        self.assertEqual(b + c, list('44445'))
        self.assertEqual(b + d, list('444x'))
        # should fail if we add the constraint back
        b.constraint = {'4': 1, 5: 2}
        self.assertRaises(ConstraintError, b.__add__, c)

    def test_iadd_prevents_bad_data(self):
        """ConstrainedList should allow in-place addition only of compliant data"""
        a = ConstrainedList('12', '123')
        a += '2'
        self.assertEqual(a, list('122'))
        self.assertEqual(a.constraint, '123')
        self.assertRaises(ConstraintError, a.__iadd__, '4')

    def test_imul(self):
        """ConstrainedList imul should preserve constraint"""
        a = ConstrainedList('12', '123')
        a *= 3
        self.assertEqual(a, list('121212'))
        self.assertEqual(a.constraint, '123')

    def test_mul(self):
        """ConstrainedList mul should preserve constraint"""
        a = ConstrainedList('12', '123')
        b = a * 3
        self.assertEqual(b, list('121212'))
        self.assertEqual(b.constraint, '123')

    def test_rmul(self):
        """ConstrainedList rmul should preserve constraint"""
        a = ConstrainedList('12', '123')
        b = 3 * a
        self.assertEqual(b, list('121212'))
        self.assertEqual(b.constraint, '123')

    def test_setitem(self):
        """ConstrainedList setitem should work only if item in constraint"""
        a = ConstrainedList('12', '123')
        a[0] = '3'
        self.assertEqual(a, list('32'))
        self.assertRaises(ConstraintError, a.__setitem__, 0, 3)
        a = ConstrainedList('1' * 20, '123')
        self.assertRaises(ConstraintError, a.__setitem__, slice(0, 1, 1), [3])
        self.assertRaises(ConstraintError, a.__setitem__,
                          slice(0, 1, 1), ['111'])
        a[2:9:2] = '3333'
        self.assertEqual(a, list('11313131311111111111'))

    def test_append(self):
        """ConstrainedList append should work only if item in constraint"""
        a = ConstrainedList('12', '123')
        a.append('3')
        self.assertEqual(a, list('123'))
        self.assertRaises(ConstraintError, a.append, 3)

    def test_extend(self):
        """ConstrainedList extend should work only if all items in constraint"""
        a = ConstrainedList('12', '123')
        a.extend('321')
        self.assertEqual(a, list('12321'))
        self.assertRaises(ConstraintError, a.extend, ['1', '2', 3])

    def test_insert(self):
        """ConstrainedList insert should work only if item in constraint"""
        a = ConstrainedList('12', '123')
        a.insert(0, '2')
        self.assertEqual(a, list('212'))
        self.assertRaises(ConstraintError, a.insert, 0, [2])

    def test_getslice(self):
        """ConstrainedList getslice should remember constraint"""
        a = ConstrainedList('123333', '12345')
        b = a[2:4]
        self.assertEqual(b, list('33'))
        self.assertEqual(b.constraint, '12345')

    def test_setslice(self):
        """ConstrainedList setslice should fail if slice has invalid chars"""
        a = ConstrainedList('123333', '12345')
        a[2:4] = ['2', '2']
        self.assertEqual(a, list('122233'))
        self.assertRaises(ConstraintError, a.__setslice__, 2, 4, [2, 2])
        a[:] = []
        self.assertEqual(a, [])
        self.assertEqual(a.constraint, '12345')

    def test_setitem_masks(self):
        """ConstrainedList setitem with masks should transform input"""
        a = ConstrainedList('12333', list(range(5)), lambda x: int(x) + 1)
        self.assertEqual(a, [2, 3, 4, 4, 4])
        self.assertRaises(ConstraintError, a.append, 4)
        b = a[1:3]
        assert b.mask is a.mask
        assert '1' not in a
        assert '2' not in a
        assert 2 in a
        assert 'x' not in a


class MappedListTests(TestCase):
    """MappedList should behave like ConstrainedList, but map items."""

    def test_setitem_masks(self):
        """MappedList setitem with masks should transform input"""
        a = MappedList('12333', list(range(5)), lambda x: int(x) + 1)
        self.assertEqual(a, [2, 3, 4, 4, 4])
        self.assertRaises(ConstraintError, a.append, 4)
        b = a[1:3]
        assert b.mask is a.mask
        assert '1' in a
        assert 'x' not in a


class ConstrainedDictTests(TestCase):
    """Tests that bad data can't sneak into ConstrainedDicts."""

    def test_init_good_data(self):
        """ConstrainedDict should init OK if list matches constraint"""
        self.assertEqual(ConstrainedDict(dict.fromkeys('abc'), 'abcd'),
                         dict.fromkeys('abc'))
        self.assertEqual(ConstrainedDict('', 'abcd'), dict(''))
        items = [1, 2, 3.2234, tuple('xyz')]
        # should accept anything dict() does if no constraint is passed
        self.assertEqual(ConstrainedDict(dict.fromkeys(items)),
                         dict.fromkeys(items))
        self.assertEqual(ConstrainedDict(dict.fromkeys(items), None),
                         dict.fromkeys(items))
        self.assertEqual(ConstrainedDict([(x, 1) for x in '12345']),
                         dict.fromkeys('12345', 1))
        # check that list is formatted correctly and chars are all there
        test_dict = dict.fromkeys('12345')
        self.assertEqual(ConstrainedDict(test_dict, '12345'), test_dict)

    def test_init_sequence(self):
        """ConstrainedDict should init from sequence, unlike normal dict"""
        self.assertEqual(ConstrainedDict('abcda'), {
                         'a': 2, 'b': 1, 'c': 1, 'd': 1})

    def test_init_bad_data(self):
        """ConstrainedDict should fail init with items not in constraint"""
        self.assertRaises(ConstraintError, ConstrainedDict,
                          dict.fromkeys('1234'), '123')
        self.assertRaises(ConstraintError, ConstrainedDict,
                          dict.fromkeys([1, 2, 3]), ['1', '2', '3'])

    def test_setitem(self):
        """ConstrainedDict setitem should work only if key in constraint"""
        a = ConstrainedDict(dict.fromkeys('12'), '123')
        a['1'] = '3'
        self.assertEqual(a, {'1': '3', '2': None})
        self.assertRaises(ConstraintError, a.__setitem__, 1, '3')

    def test_copy(self):
        """ConstrainedDict copy should retain constraint"""
        a = ConstrainedDict(dict.fromkeys('12'), '123')
        b = a.copy()
        self.assertEqual(a.constraint, b.constraint)
        self.assertRaises(ConstraintError, a.__setitem__, 1, '3')
        self.assertRaises(ConstraintError, b.__setitem__, 1, '3')

    def test_fromkeys(self):
        """ConstrainedDict instance fromkeys should retain constraint"""
        a = ConstrainedDict(dict.fromkeys('12'), '123')
        b = a.fromkeys('23')
        self.assertEqual(a.constraint, b.constraint)
        self.assertRaises(ConstraintError, a.__setitem__, 1, '3')
        self.assertRaises(ConstraintError, b.__setitem__, 1, '3')
        b['2'] = 5
        self.assertEqual(b, {'2': 5, '3': None})

    def test_setdefault(self):
        """ConstrainedDict setdefault shouldn't allow bad keys"""
        a = ConstrainedDict({'1': None, '2': 'xyz'}, '123')
        self.assertEqual(a.setdefault('2', None), 'xyz')
        self.assertEqual(a.setdefault('1', None), None)
        self.assertRaises(ConstraintError, a.setdefault, 'x', 3)
        a.setdefault('3', 12345)
        self.assertEqual(a, {'1': None, '2': 'xyz', '3': 12345})

    def test_update(self):
        """ConstrainedDict should allow update only of compliant data"""
        a = ConstrainedDict(dict.fromkeys('123'), '12345')
        b = ConstrainedDict(dict.fromkeys('444'), '4')
        c = ConstrainedDict(dict.fromkeys('45'), '12345')
        d = ConstrainedDict([['x', 'y']])
        a.update(b)
        self.assertEqual(a, dict.fromkeys('1234'))
        a.update(c)
        self.assertEqual(a, dict.fromkeys('12345'))
        self.assertRaises(ConstraintError, b.update, c)
        self.assertRaises(ConstraintError, c.update, d)
        # should be OK if constraint removed
        b.constraint = None
        b.update(c)
        self.assertEqual(b, dict.fromkeys('45'))
        b.update(d)
        self.assertEqual(b, {'4': None, '5': None, 'x': 'y'})
        # should fail if we add the constraint back
        b.constraint = {'4': 1, 5: 2, '5': 1, 'x': 1}
        self.assertRaises(ConstraintError, b.update, {4: 1})
        b.update({5: 1})
        self.assertEqual(b, {'4': None, '5': None, 'x': 'y', 5: 1})

    def test_setitem_masks(self):
        """ConstrainedDict setitem should work only if key in constraint"""
        key_mask = str

        def val_mask(x): return int(x) + 3
        d = ConstrainedDict({1: 4, 2: 6}, '123', key_mask, val_mask)
        d[1] = '456'
        self.assertEqual(d, {'1': 459, '2': 9, })
        d['1'] = 234
        self.assertEqual(d, {'1': 237, '2': 9, })
        self.assertRaises(ConstraintError, d.__setitem__, 4, '3')
        e = d.copy()
        assert e.mask is d.mask
        assert '1' in d
        assert not 1 in d


class MappedDictTests(TestCase):
    """MappedDict should work like ConstrainedDict, but map keys."""

    def test_setitem_masks(self):
        """MappedDict setitem should work only if key in constraint"""
        key_mask = str

        def val_mask(x): return int(x) + 3
        d = MappedDict({1: 4, 2: 6}, '123', key_mask, val_mask)
        d[1] = '456'
        self.assertEqual(d, {'1': 459, '2': 9, })
        d['1'] = 234
        self.assertEqual(d, {'1': 237, '2': 9, })
        self.assertRaises(ConstraintError, d.__setitem__, 4, '3')
        e = d.copy()
        assert e.mask is d.mask
        assert '1' in d
        assert 1 in d
        assert 1 not in list(d.keys())
        assert 'x' not in list(d.keys())

    def test_getitem(self):
        """MappedDict getitem should automatically map key."""
        key_mask = str
        d = MappedDict({}, '123', key_mask)
        self.assertEqual(d, {})
        d['1'] = 5
        self.assertEqual(d, {'1': 5})
        self.assertEqual(d[1], 5)

    def test_get(self):
        """MappedDict get should automatically map key."""
        key_mask = str
        d = MappedDict({}, '123', key_mask)
        self.assertEqual(d, {})
        d['1'] = 5
        self.assertEqual(d, {'1': 5})
        self.assertEqual(d.get(1, 'x'), 5)
        self.assertEqual(d.get(5, 'x'), 'x')

    def test_has_key(self):
        """MappedDict has_key should automatically map key."""
        key_mask = str
        d = MappedDict({}, '123', key_mask)
        self.assertEqual(d, {})
        d['1'] = 5
        assert '1' in d
        assert 1 in d
        assert '5' not in d


class reverse_complementTests(TestCase):
    """Tests of the public reverse_complement function"""

    def test_reverse_complement_DNA(self):
        """reverse_complement should correctly return reverse complement of DNA"""

        # input and correct output taken from example at
        # http://bioweb.uwlax.edu/GenWeb/Molecular/Seq_Anal/
        # Reverse_Comp/reverse_comp.html
        user_input = "ATGCAGGGGAAACATGATTCAGGAC"
        correct_output = "GTCCTGAATCATGTTTCCCCTGCAT"
        real_output = reverse_complement(user_input)
        self.assertEqual(real_output, correct_output)

    # end test_reverse_complement_DNA

    def test_reverse_complement_RNA(self):
        """reverse_complement should correctly return reverse complement of RNA"""

        # input and correct output taken from test_reverse_complement_DNA test,
        # with all Ts changed to Us
        user_input = "AUGCAGGGGAAACAUGAUUCAGGAC"
        correct_output = "GUCCUGAAUCAUGUUUCCCCUGCAU"

        # remember to use False toggle to get RNA instead of DNA
        real_output = reverse_complement(user_input, False)
        self.assertEqual(real_output, correct_output)
    # end test_reverse_complement_RNA

    def test_reverse_complement_caseSensitive(self):
        """reverse_complement should convert bases without changing case"""

        user_input = "aCGtAcgT"
        correct_output = "AcgTaCGt"
        real_output = reverse_complement(user_input)
        self.assertEqual(real_output, correct_output)
    # end test_reverse_complement_caseSensitive

    def test_reverse_complement_nonNucleicSeq(self):
        """reverse_complement should just reverse any chars but ACGT/U"""

        user_input = "BDeF"
        self.assertRaises(ValueError, reverse_complement, user_input)
    # end test_reverse_complement_nonNucleicSeq

    def test_reverse_complement_emptySeq(self):
        """reverse_complement should return empty string if given empty sequence"""

        # shouldn't matter whether in DNA or RNA mode
        real_output = reverse_complement("")
        self.assertEqual(real_output, "")
    # end test_reverse_complement_emptySeq

    def test_reverse_complement_noSeq(self):
        """reverse_complement should return error if given no sequence argument"""

        self.assertRaises(TypeError, reverse_complement)
    # end test_reverse_complement_noSeq
# end reverse_complementTests

    def test_not_none(self):
        """not_none should return True if none of the items is None"""
        assert not_none([1, 2, 3, 4])
        assert not not_none([1, 2, 3, None])
        self.assertEqual(list(filter(not_none, [(1, 2), (3, None)])), [(1, 2)])
    # end test_not_none

    def test_NestedSplitter(self):
        """NestedSplitter should make a function which return expected list"""
        # test delimiters, constructor, filter_
        line = 'ii=0; oo= 9, 6 5;  ; xx=  8;  '
        cmds = [
            "NestedSplitter(';=,')(line)",
            "NestedSplitter([';', '=', ','])(line)",
            "NestedSplitter([(';'), '=', ','], constructor=None)(line)",
            "NestedSplitter([(';'), '=', ','], filter_=None)(line)",
            "NestedSplitter([(';',1), '=', ','])(line)",
            "NestedSplitter([(';',-1), '=', ','])(line)"
        ]
        results = [
            [['ii', '0'], ['oo', ['9', '6 5']], '', ['xx', '8'], ''],
            [['ii', '0'], ['oo', ['9', '6 5']], '', ['xx', '8'], ''],
            [['ii', '0'], [' oo', [' 9', ' 6 5']], '  ', [' xx', '  8'], '  '],
            [['ii', '0'], ['oo', ['9', '6 5']], ['xx', '8']],
            [['ii', '0'], ['oo', ['9', '6 5;  ; xx'], '8;']],
            [['ii', '0; oo', ['9', '6 5;  ; xx'], '8'], '']
        ]
        for cmd, result in zip(cmds, results):
            self.assertEqual(eval(cmd), result)

        # test uncontinous level of delimiters
        test = 'a; b,c; d,e:f; g:h;'  # g:h should get [[g,h]] instead of [g,h]
        self.assertEqual(NestedSplitter(';,:')(test),
                         ['a', ['b', 'c'], ['d', ['e', 'f']], [['g', 'h']], ''])

        # test empty
        self.assertEqual(NestedSplitter(';,:')(''), [''])
        self.assertEqual(NestedSplitter(';,:')('  '), [''])
        self.assertEqual(NestedSplitter(';,:', filter_=None)(' ;, :'), [[[]]])

    def test_curry(self):
        """curry should generate the function with parameters setted"""
        curry_test = curry(lambda x, y: x == y, 5)
        knowns = ((3, False),
                  (9, False),
                  (5, True))
        for arg2, result in knowns:
            self.assertEqual(curry_test(arg2), result)


if __name__ == '__main__':
    main()
