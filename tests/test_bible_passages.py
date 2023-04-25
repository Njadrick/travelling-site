from kanisa.models.bible import bible
from kanisa.models.bible.bible_constants import MULTI_CHAPTER_BOOKS
from kanisa.models.sermons import SermonSeries
from django.core import serializers
from django.test import TestCase


class BiblePassageBadInput(TestCase):
    def test_invalid_arguments(self):
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          'foo')
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 2, 3, 1, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 2, 4, 2, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peters')
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 'foo')
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 3, 'bar')
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 3, 4, 'bar', 5)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 3, 4, 4, 'baz')
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 3, None, 4, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', 3, 1, 4, None)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, 4, None, None)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, 1, 2, None)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, 1, None, 2)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, 1, 2, 3)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, None, 4, None)
        self.assertRaises(bible.InvalidPassage, bible.BiblePassage,
                          '1 Peter', None, None, None, 4)

    def test_out_of_range(self):
        self.assertRaises(bible.BookBoundsError, bible.BiblePassage,
                          'Matthew', 29)
        self.assertRaises(bible.BookBoundsError, bible.BiblePassage,
                          'Psalm', 151)
        self.assertRaises(bible.BookBoundsError, bible.to_passage,
                          'Revelation 1-23')
        self.assertRaises(bible.BookBoundsError, bible.to_passage,
                          'Revelation 23-24')
        self.assertRaises(bible.ChapterBoundsError, bible.BiblePassage,
                          'Revelation', 22, 22)
        self.assertRaises(bible.ChapterBoundsError, bible.to_passage,
                          'Revelation 22:20-22')


class BiblePassage(TestCase):
    def test_to_string(self):
        self.assertEqual(unicode(bible.to_passage('1 thessalonians')),
                         '1 Thessalonians')
        self.assertEqual(unicode(bible.to_passage('1 thessalonians  3')),
                         '1 Thessalonians 3')
        self.assertEqual(unicode(bible.to_passage('1 thessalonians 3 v 8')),
                         '1 Thessalonians 3:8')
        bit_too_long = unicode(bible.to_passage('1 thessalonians 3 v 8 - 4:1'))
        self.assertEqual(bit_too_long,
                         '1 Thessalonians 3:8-4:1')
        self.assertEqual(unicode(bible.to_passage('1 th 3 v 8 - 3:9')),
                         '1 Thessalonians 3:8-9')
        self.assertEqual(unicode(bible.to_passage('1 cor')),
                         '1 Corinthians')
        self.assertEqual(unicode(bible.to_passage('1 cor 2')),
                         '1 Corinthians 2')
        self.assertEqual(unicode(bible.to_passage('1 cor 2:3-7')),
                         '1 Corinthians 2:3-7')
        self.assertEqual(unicode(bible.to_passage('1 cor 2-3')),
                         '1 Corinthians 2-3')

    def test_length(self):
        self.assertEqual(len(bible.to_passage('1 cor 2 v 3 - 7')),
                         len('1 Corinthians 2:3-7'))
        self.assertEqual(len(bible.to_passage('1 cor 2-3')),
                         len('1 Corinthians 2-3'))


class ToPassageBadInput(TestCase):
    def test_non_string(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage, 4000)

    def test_non_book(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage, 'foo')

    def test_invalid_range(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage,
                          '1 Thessalonians 2:1 - 1v2')
        self.assertRaises(bible.InvalidPassage, bible.to_passage,
                          '1 Thessalonians 2-1')
        self.assertRaises(bible.InvalidPassage, bible.to_passage,
                          '1 Thessalonians 2:2-2:1')

    def test_good_book_stupid_range(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage,
                          '1 Thessalonians Fish')


class ToPassageGoodInput(TestCase):
    def test_books_only(self):
        for b in bible.BOOKS_OF_THE_BIBLE:
            passage = bible.to_passage(b)
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, None)
            self.assertEqual(passage.start_verse, None)
            self.assertEqual(passage.end_chapter, None)
            self.assertEqual(passage.end_verse, None)

    def test_uppercase_books_only(self):
        for b in bible.BOOKS_OF_THE_BIBLE:
            passage = bible.to_passage(b.upper())
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, None)
            self.assertEqual(passage.start_verse, None)
            self.assertEqual(passage.end_chapter, None)
            self.assertEqual(passage.end_verse, None)

    def test_lower_case_full_passage(self):
        passage = bible.to_passage('1 thessalonians 3:1-4:5')
        self.assertEqual(passage.book, '1 Thessalonians')
        self.assertEqual(passage.start_chapter, 3)
        self.assertEqual(passage.start_verse, 1)
        self.assertEqual(passage.end_chapter, 4)
        self.assertEqual(passage.end_verse, 5)

    def test_books_with_chapter_one(self):
        for b in MULTI_CHAPTER_BOOKS:
            passage = bible.to_passage(b + ' 1')
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, 1)
            self.assertEqual(passage.start_verse, None)
            self.assertEqual(passage.end_chapter, None)
            self.assertEqual(passage.end_verse, None)

    def test_books_with_chapter_one_to_two(self):
        for b in MULTI_CHAPTER_BOOKS:
            passage = bible.to_passage(b + ' 1 - 2')
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, 1)
            self.assertEqual(passage.start_verse, None)
            self.assertEqual(passage.end_chapter, 2)
            self.assertEqual(passage.end_verse, None)

    def test_books_with_chapter_one_verse_one(self):
        for b in bible.BOOKS_OF_THE_BIBLE:
            passage = bible.to_passage(b + ' 1:2')
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, 1)
            self.assertEqual(passage.start_verse, 2)
            self.assertEqual(passage.end_chapter, None)
            self.assertEqual(passage.end_verse, None)

            passage2 = bible.to_passage(b + ' 1 v 2')
            self.assertEqual(passage2.book, b)
            self.assertEqual(passage2.start_chapter, 1)
            self.assertEqual(passage2.start_verse, 2)
            self.assertEqual(passage2.end_chapter, None)
            self.assertEqual(passage2.end_verse, None)

    def test_books_with_chapter_and_verse_range(self):
        for b in bible.BOOKS_OF_THE_BIBLE:
            passage = bible.to_passage(b + ' 1:1-2')
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, 1)
            self.assertEqual(passage.start_verse, 1)
            self.assertEqual(passage.end_chapter, 1)
            self.assertEqual(passage.end_verse, 2)

            passage2 = bible.to_passage(b + ' 1 v 1 - 2')
            self.assertEqual(passage2.book, b)
            self.assertEqual(passage2.start_chapter, 1)
            self.assertEqual(passage2.start_verse, 1)
            self.assertEqual(passage2.end_chapter, 1)
            self.assertEqual(passage2.end_verse, 2)

    def test_books_with_full_range(self):
        for b in MULTI_CHAPTER_BOOKS:
            passage = bible.to_passage(b + ' 1:3-2:4')
            self.assertEqual(passage.book, b)
            self.assertEqual(passage.start_chapter, 1)
            self.assertEqual(passage.start_verse, 3)
            self.assertEqual(passage.end_chapter, 2)
            self.assertEqual(passage.end_verse, 4)

            passage2 = bible.to_passage(b + ' 1 v 3 - 2 v 4')
            self.assertEqual(passage2.book, b)
            self.assertEqual(passage2.start_chapter, 1)
            self.assertEqual(passage2.start_verse, 3)
            self.assertEqual(passage2.end_chapter, 2)
            self.assertEqual(passage2.end_verse, 4)

    def test_book_pseudonyms(self):
        self.assertEqual(bible.normalise_passage('Psalms 23:1-6'),
                         'Psalm 23:1-6')
        self.assertEqual(bible.normalise_passage('1 Jn 4:1-5'),
                         '1 John 4:1-5')
        self.assertEqual(bible.normalise_passage('Song of Songs 4:2'),
                         'Song of Solomon 4:2')
        self.assertEqual(bible.normalise_passage('Sos 4:2'),
                         'Song of Solomon 4:2')
        self.assertEqual(bible.normalise_passage('Eph 4:2'),
                         'Ephesians 4:2')
        self.assertEqual(bible.normalise_passage('1 Jo 3:2'),
                         '1 John 3:2')
        self.assertEqual(bible.normalise_passage('1 Jo 1:1-5:5'),
                         '1 John 1:1-5:5')

    def test_ambiguous_names(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage, 'J 3:16')
        self.assertRaises(bible.InvalidPassage, bible.to_passage, 'Ez 3:16')

    def test_overly_long_names(self):
        self.assertRaises(bible.InvalidPassage, bible.to_passage, 'Johns 3:16')

    def test_less_likely_inputs(self):
        passage = bible.to_passage('1 John ch 2 v 3-5')
        self.assertEqual(unicode(passage), '1 John 2:3-5')

        passage = bible.to_passage('1 John chapter 2 v 3-5')
        self.assertEqual(unicode(passage), '1 John 2:3-5')

        passage = bible.to_passage('1 John chapter 2 verse 3 - v5')
        self.assertEqual(unicode(passage), '1 John 2:3-5')

        passage = bible.to_passage('1 John ch 2 v 3 - ch 4:5')
        self.assertEqual(unicode(passage), '1 John 2:3-4:5')

    def test_same_start_and_end_chapter(self):
        passage = bible.to_passage('1 John 1-1')
        self.assertEqual(unicode(passage), '1 John 1')

        passage = bible.to_passage('1 John 1:3-1:4')
        self.assertEqual(unicode(passage), '1 John 1:3-4')

    def test_single_chapter_books(self):
        passage = bible.to_passage('Jude 1:2-3')
        self.assertEqual(passage.book, 'Jude')
        self.assertEqual(passage.start_chapter, 1)
        self.assertEqual(passage.end_chapter, 1)
        self.assertEqual(passage.start_verse, 2)
        self.assertEqual(passage.end_verse, 3)
        self.assertEqual(unicode(passage), 'Jude 2-3')

        passage = bible.to_passage('Obadiah 1:2-1:3')
        self.assertEqual(passage.book, 'Obadiah')
        self.assertEqual(passage.start_chapter, 1)
        self.assertEqual(passage.end_chapter, 1)
        self.assertEqual(passage.start_verse, 2)
        self.assertEqual(passage.end_verse, 3)
        self.assertEqual(unicode(passage), 'Obadiah 2-3')

        passage = bible.to_passage('Philemon 2-3')
        self.assertEqual(passage.book, 'Philemon')
        self.assertEqual(passage.start_chapter, 1)
        self.assertEqual(passage.end_chapter, 1)
        self.assertEqual(passage.start_verse, 2)
        self.assertEqual(passage.end_verse, 3)
        self.assertEqual(unicode(passage), 'Philemon 2-3')

        passage = bible.to_passage('2 Jo 1')
        self.assertEqual(passage.book, '2 John')
        self.assertEqual(passage.start_chapter, 1)
        self.assertEqual(passage.end_chapter, None)
        self.assertEqual(passage.start_verse, 1)
        self.assertEqual(passage.end_verse, None)
        self.assertEqual(unicode(passage), '2 John 1')

        self.assertRaises(bible.ChapterBoundsError, bible.to_passage,
                          '2 John 1-14')
        self.assertRaises(bible.ChapterBoundsError, bible.to_passage,
                          '2 John 14')
        self.assertRaises(bible.ChapterBoundsError, bible.to_passage,
                          '2 John 14-15')
        self.assertRaises(bible.BookBoundsError, bible.to_passage,
                          '2 John 1:1-2:1')
        self.assertRaises(bible.BookBoundsError, bible.to_passage,
                          '2 John 2:1-2')
        self.assertRaises(bible.BookBoundsError, bible.to_passage,
                          '2 John 2:1-2:2')

    def test_common_names(self):
        COMMON_ABBREVIATIONS = [['gen', ],
                                ['ex', ],
                                ['lev', ],
                                ['num', ],
                                ['deut', ],
                                ['jos', 'josh', ],
                                # Not sure how people abbreviate Judges
                                [],
                                # Not sure how people abbreviate Ruth
                                [],
                                ['1 sam', ],
                                ['2 sam', ],
                                ['1 ki', '1 kgs', ],
                                ['2 ki', '2 kgs', ],
                                ['1 chr', ],
                                ['2 chr', ],
                                # Not sure how people abbreviate Ezra
                                [],
                                ['neh', ],
                                # Not sure how people abbreviate Esther
                                [],
                                # Not sure how people abbreviate Job
                                [],
                                ['ps', ],
                                ['Pr', ],
                                ['Ecc', ],
                                ['SoS', 'SS'],
                                ['Is', ],
                                ['Jer', ],
                                ['Lam', ],
                                ['Eze', ],
                                ['Dan', ],
                                ['Hos', ],
                                # Not sure how people abbreviate Joel
                                [],
                                # Not sure how people abbreviate Amos
                                [],
                                ['Oba', ],
                                ['Jon', ],
                                ['Mic', ],
                                ['Nah', ],
                                ['Hab', ],
                                ['Zep', 'Zeph', ],
                                ['Hag', ],
                                ['Zec', 'Zech', ],
                                ['Mal', ],
                                ['Mt', 'Matt', ],
                                ['Mk', 'Mar', ],
                                ['Lk', ],
                                ['Joh', 'Jn', ],
                                ['Acts', ],
                                ['Rom', ],
                                ['1 Cor', '1 co', ],
                                ['2 Cor', '2 co'],
                                ['Gal', ],
                                ['Eph', ],
                                # This clashes with Philemon, but people tend
                                # to mean Philippians
                                ['Phil', ],
                                ['Col', ],
                                ['1 Th', '1 thes', '1 thess'],
                                ['2 Th', '2 thes', '2 thess'],
                                ['1 tim', ],
                                ['2 tim', ],
                                ['Tit', ],
                                # Not sure how people abbreviate Philemon
                                [],
                                ['Heb', ],
                                ['Jam', 'Jas', ],
                                ['1 Pet', ],
                                ['2 Pet', ],
                                ['1 Jn', '1 Jo', ],
                                ['2 Jn', '2 Jo', ],
                                ['3 Jn', '3 Jo', ],
                                ['Jude', ],
                                ['Rev', ]]

        for i in range(0, len(COMMON_ABBREVIATIONS)):
            for abbr in COMMON_ABBREVIATIONS[i]:
                reference = bible.normalise_book(bible.BOOKS_OF_THE_BIBLE[i])
                self.assertEqual(unicode(bible.to_passage(abbr)),
                                 reference)


class BiblePassageModelField(TestCase):
    def test_assign_passage(self):
        p = bible.to_passage('2 John 1')
        m = SermonSeries(passage=p, title='test_title', slug='test-title')
        m.save()
        self.assertEqual(m.passage, p)
        self.assertEqual(m._meta.get_field("passage").verbose_name,
                         "passage")
        self.assertTrue(isinstance(p, bible.BiblePassage))
        self.assertTrue(isinstance(m.passage, bible.BiblePassage))

        m1 = SermonSeries.objects.get(pk=m.pk)
        self.assertTrue(isinstance(m1.passage, bible.BiblePassage))
        self.assertEqual(unicode(m1.passage), '2 John 1')

    def test_assign_string_to_model(self):
        p = 'Psalm'
        m = SermonSeries(passage=p, title='test_title', slug='test-title')
        m.save()

        m1 = SermonSeries.objects.get(pk=m.pk)
        self.assertTrue(isinstance(m1.passage, bible.BiblePassage))
        self.assertEqual(unicode(m1.passage), 'Psalms')

    def test_serialization(self):
        p = 'Psalm'
        m = SermonSeries(passage=p, title='test_title', slug='test-title')
        m.save()

        cereal = serializers.serialize('json',
                                       SermonSeries.objects.all())
        objects = list(serializers.deserialize("json", cereal))
        self.assertEqual(len(objects), 1)
        self.assertEqual(unicode(objects[0].object.passage),
                         'Psalms')

    def test_none(self):
        m = SermonSeries(title='test_title', slug='test-title')
        m.save()

        m1 = SermonSeries.objects.get(pk=m.pk)
        self.assertEqual(m1.passage, None)

    def test_bad_passage_saved_as_string(self):
        m = SermonSeries(title='test_title', slug='test-title')
        m.passage = 'Not a Bible Passage'
        m.save()

        m1 = SermonSeries.objects.get(pk=m.pk)
        self.assertEqual(m1.passage, None)
