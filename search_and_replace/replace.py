#!/bin/python

from zdesk import Zendesk
import os
import sys
import argparse

def query_yes_no(question, default="no"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

parser = argparse.ArgumentParser(description='Search and replace for zendesk help center articles and translations')
parser.add_argument('-l', '--locale', metavar='LOCALE', type=str, help='The locale to search, usually fr, en or es')
parser.add_argument('-u', '--username', metavar='USERNAME', type=str, help='Username, usually the email address')
parser.add_argument('-t', '--token', metavar='TOKEN', type=str, help='API token')
parser.add_argument('--url', metavar='URL', type=str, help='Url endpoint of the help center i.e. https://buritoes.zendesk.com/')
parser.add_argument('--old', metavar='OLD', type=str, nargs='*', help='Word that needs replacement')
parser.add_argument('--new', metavar='NEW', type=str, nargs='*', help='New word that will replace old word')
parser.add_argument('--ask', help='Ask before applying the change', action='store_true')
parser.add_argument('-d', '--dry-run', action='store_true')
parser.add_argument('-v', '--verbose', action='store_true')
args = parser.parse_args()

if len(args.old) != len(args.new):
  print('OLD must have the same number of argument than NEW')
  sys.exit(1)

zendesk = Zendesk(zdesk_url=args.url, zdesk_email=args.username, zdesk_password=args.token, zdesk_token=True)

page = 1
articles = zendesk.help_center_articles_list(per_page=100, page=page)
if args.ask and not query_yes_no('Found "' + str(articles['count']) + '". Do you want to keep going?'):
  sys.exit(1)

while True:
  for article in articles['articles']:
    translations = zendesk.help_center_article_translations(article_id=article['id'], locales=args.locale)
    for translation in translations['translations']:
      for i in range(0, len(args.old)):
        if translation['body'] is None or args.old[i] not in translation['body']:
          continue

        print('='*200)
        print(translation['body'])

        translation['body'] = translation['body'].replace(args.old[i], args.new[i])

        print('='*200)
        print(translation['body'])

        if args.ask and not query_yes_no('> Apply this change?'):
          if not args.dry_run:
            zendesk.help_center_article_translation_update(article_id=article['id'], locale=args.locale, data=translation)

  if(articles['next_page'] is None):
    break
  page += 1
  articles = zendesk.help_center_articles_list(per_page=100, page=page)

sys.exit(0)

