# def test_filter(self):
#     Poll.objects.create(question='Sup?', pub_date=timezone.now())
#     Poll.objects.create(question='How you doing?', pub_date=timezone.now() - datetime.timedelta(days=1))

#     filter = admin.WasPublishedRecentlyFilter(None, {'published_recently':'yes'}, Poll, admin.PollAdmin)
#     poll = filter.queryset(None, Poll.objects.all())[0]
#     self.assertEqual(poll.question, 'Sup?')

#     filter = admin.WasPublishedRecentlyFilter(None, {'published_recently':'no'}, Poll, admin.PollAdmin)
#     poll = filter.queryset(None, Poll.objects.all())[0]
#     self.assertEqual(poll.question, 'How you doing?')


