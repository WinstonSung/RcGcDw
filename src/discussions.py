# -*- coding: utf-8 -*-

# Recent changes Goat compatible Discord webhook is a project for using a webhook as recent changes page from MediaWiki.
# Copyright (C) 2020 Frisk

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging, schedule, requests
from typing import Dict, Any

from src.configloader import settings

from src.discussion_formatters import embed_formatter, compact_formatter
from src.misc import datafile, prepare_paths
from src.discord.queue import messagequeue
from src.session import session
from src.exceptions import ArticleCommentError

# Create a custom logger

discussion_logger = logging.getLogger("rcgcdw.disc")

# Create a variable in datafile if it doesn't exist yet (in files <1.10)

if "discussion_id" not in datafile.data:
	datafile["discussion_id"] = 0
	datafile.save_datafile()

storage = datafile

fetch_url = "{wiki}wikia.php?controller=DiscussionPost&method=getPosts&sortDirection=descending&sortKey=creation_date&limit={limit}".format(wiki=settings["fandom_discussions"]["wiki_url"], limit=settings["fandom_discussions"]["limit"])
domain = prepare_paths(settings["fandom_discussions"]["wiki_url"], dry=True)  # Shutdown if the path for discussions is wrong

def fetch_discussions():
	messagequeue.resend_msgs()
	request = safe_request(fetch_url)
	if request:
		try:
			request_json = request.json()["_embedded"]["doc:posts"]
			request_json.reverse()
		except ValueError:
			discussion_logger.warning("ValueError in fetching discussions")
			return None
		except KeyError:
			discussion_logger.warning("Wiki returned %s" % (request.json()))
			return None
		else:
			if request_json:
				comment_pages: dict = {}
				comment_events: list = [post["forumId"] for post in request_json if post["_embedded"]["thread"][0]["containerType"] == "ARTICLE_COMMENT" and int(post["id"]) > storage["discussion_id"]]
				if comment_events:
					comment_pages = safe_request(
						"{wiki}wikia.php?controller=FeedsAndPosts&method=getArticleNamesAndUsernames&stablePageIds={pages}&format=json".format(
							wiki=settings["fandom_discussions"]["wiki_url"], pages=",".join(comment_events)
						))
					if comment_pages:
						try:
							comment_pages = comment_pages.json()["articleNames"]
						except ValueError:
							discussion_logger.warning("ValueError in fetching discussions")
							return None
						except KeyError:
							discussion_logger.warning("Wiki returned %s" % (request_json.json()))
							return None
					else:
						return None
				for post in request_json:
					if int(post["id"]) > storage["discussion_id"]:
						try:
							parse_discussion_post(post, comment_pages)
						except ArticleCommentError:
							return None
				if int(post["id"]) > storage["discussion_id"]:
					storage["discussion_id"] = int(post["id"])
					datafile.save_datafile()

def parse_discussion_post(post, comment_pages):
	"""Initial post recognition & handling"""
	post_type = post["_embedded"]["thread"][0]["containerType"]
	# Filter posts by forum
	if post_type == "FORUM" and settings["fandom_discussions"].get("show_forums", []):
		if not post["forumName"] in settings["fandom_discussions"]["show_forums"]:
			discussion_logger.debug(f"Ignoring post as it's from {post['forumName']}.")
			return
	comment_page = None
	if post_type == "ARTICLE_COMMENT":
		try:
			comment_page = {**comment_pages[post["forumId"]], "fullUrl": domain + comment_pages[post["forumId"]]["relativeUrl"]}
		except KeyError:
			discussion_logger.error("Could not parse paths for article comment, here is the content of comment_pages: {}, ignoring...".format(comment_pages))
			raise ArticleCommentError
	formatter(post_type, post, comment_page)


def safe_request(url):
	"""Function to assure safety of request, and do not crash the script on exceptions,"""
	try:
		request = session.get(url, timeout=10, allow_redirects=False, headers={"Accept": "application/hal+json"})
	except requests.exceptions.Timeout:
		discussion_logger.warning("Reached timeout error for request on link {url}".format(url=url))
		return None
	except requests.exceptions.ConnectionError:
		discussion_logger.warning("Reached connection error for request on link {url}".format(url=url))
		return None
	except requests.exceptions.ChunkedEncodingError:
		discussion_logger.warning("Detected faulty response from the web server for request on link {url}".format(url=url))
		return None
	else:
		if 499 < request.status_code < 600:
			return None
		return request

formatter = embed_formatter if settings["fandom_discussions"]["appearance"]["mode"] == "embed" else compact_formatter

schedule.every(settings["fandom_discussions"]["cooldown"]).seconds.do(fetch_discussions)