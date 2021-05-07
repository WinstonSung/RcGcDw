# -*- coding: utf-8 -*-

# This file is part of Recent changes Goat compatible Discord webhook (RcGcDw).

# RcGcDw is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# RcGcDw is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with RcGcDw.  If not, see <http://www.gnu.org/licenses/>.

import ipaddress
import math
import re
import time
import logging
import datetime
import json
from urllib.parse import quote_plus, quote

from bs4 import BeautifulSoup

from src.configloader import settings
from src.misc import WIKI_SCRIPT_PATH, safe_read, \
	WIKI_API_PATH, ContentParser, profile_field_name, LinkParser
from src.api.util import link_formatter, create_article_path
from src.discord.queue import send_to_discord
from src.discord.message import DiscordMessage, DiscordMessageMetadata

if AUTO_SUPPRESSION_ENABLED:
	from src.discord.redaction import delete_messages, redact_messages

from src.i18n import rc_formatters
#from src.rc import recent_changes, pull_comment
_ = rc_formatters.gettext
ngettext = rc_formatters.ngettext

logger = logging.getLogger("rcgcdw.rc_formatters")
#from src.rcgcdw import recent_changes, ngettext, logger, profile_field_name, LinkParser, pull_comment


LinkParser = LinkParser()

def format_user(change, recent_changes, action):
	if "anon" in change:
		author_url = create_article_path("Special:Contributions/{user}".format(
			user=change["user"].replace(" ", "_")))  # Replace here needed in case of #75
		logger.debug("current user: {} with cache of IPs: {}".format(change["user"], recent_changes.map_ips.keys()))
		if change["user"] not in list(recent_changes.map_ips.keys()):
			contibs = safe_read(recent_changes._safe_request(
				"{wiki}?action=query&format=json&list=usercontribs&uclimit=max&ucuser={user}&ucstart={timestamp}&ucprop=".format(
					wiki=WIKI_API_PATH, user=change["user"], timestamp=change["timestamp"])), "query", "usercontribs")
			if contibs is None:
				logger.warning(
					"WARNING: Something went wrong when checking amount of contributions for given IP address")
				if settings.get("hide_ips", False):
					change["user"] = _("Unregistered user")
				change["user"] = change["user"] + "(?)"
			else:
				recent_changes.map_ips[change["user"]] = len(contibs)
				logger.debug(
					"Current params user {} and state of map_ips {}".format(change["user"], recent_changes.map_ips))
				if settings.get("hide_ips", False):
					change["user"] = _("Unregistered user")
				change["user"] = "{author} ({contribs})".format(author=change["user"], contribs=len(contibs))
		else:
			logger.debug(
				"Current params user {} and state of map_ips {}".format(change["user"], recent_changes.map_ips))
			if action in ("edit", "new"):
				recent_changes.map_ips[change["user"]] += 1
			change["user"] = "{author} ({amount})".format(author=change["user"] if settings.get("hide_ips", False) is False else _("Unregistered user"),
			                                              amount=recent_changes.map_ips[change["user"]])
	else:
		author_url = create_article_path("User:{}".format(change["user"].replace(" ", "_")))
	return change["user"], author_url


def compact_formatter(action, change, parsed_comment, categories, recent_changes):
	request_metadata = DiscordMessageMetadata("POST", rev_id=change.get("revid", None), log_id=change.get("logid", None), page_id=change.get("pageid", None))
	if action != "suppressed":
		author_url = link_formatter(create_article_path("User:{user}".format(user=change["user"])))
		if "anon" in change:
			change["user"] = _("Unregistered user")
			author = change["user"]
		else:
			author = change["user"]
	parsed_comment = "" if parsed_comment is None else " *("+parsed_comment+")*"
	if action in ["edit", "new"]:
	elif action =="upload/upload":

	elif action == "upload/revert":

	elif action == "upload/overwrite":

	elif action == "delete/delete":

	elif action == "delete/delete_redir":

	elif action == "move/move":

	elif action == "move/move_redir":

	elif action == "protect/move_prot":

	elif action == "block/block":

	elif action == "block/reblock":

	elif action == "block/unblock":

	elif action == "curseprofile/comment-created":
		link = link_formatter(create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"])))
		target_user = change["title"].split(':', 1)[1]
		if target_user != author:
			content = _("[{author}]({author_url}) left a [comment]({comment}) on {target}'s profile".format(author=author, author_url=author_url, comment=link, target=target_user))
		else:
			content = _("[{author}]({author_url}) left a [comment]({comment}) on their own profile".format(author=author, author_url=author_url, comment=link))
	elif action == "curseprofile/comment-replied":
		link = link_formatter(create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"])))
		target_user = change["title"].split(':', 1)[1]
		if target_user != author:
			content = _(
				"[{author}]({author_url}) replied to a [comment]({comment}) on {target}'s profile".format(author=author,
				                                                                                    author_url=author_url,
				                                                                                    comment=link,
				                                                                                    target=target_user))
		else:
			content = _(
				"[{author}]({author_url}) replied to a [comment]({comment}) on their own profile".format(author=author,
				                                                                                   comment=link,
				                                                                                   author_url=author_url))
	elif action == "curseprofile/comment-edited":
		link = link_formatter(create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"])))
		target_user = change["title"].split(':', 1)[1]
		if target_user != author:
			content = _(
				"[{author}]({author_url}) edited a [comment]({comment}) on {target}'s profile".format(author=author,
				                                                                                          author_url=author_url,
				                                                                                          comment=link,
				                                                                                          target=target_user))
		else:
			content = _(
				"[{author}]({author_url}) edited a [comment]({comment}) on their own profile".format(author=author,
				                                                                                         comment=link,
				                                                                                         author_url=author_url))
	elif action == "curseprofile/comment-purged":
		target_user = change["title"].split(':', 1)[1]
		if target_user != author:
			content = _("[{author}]({author_url}) purged a comment on {target}'s profile".format(author=author, author_url=author_url,target=target_user))
		else:
			content = _("[{author}]({author_url}) purged a comment on their own profile".format(author=author, author_url=author_url))
	elif action == "curseprofile/comment-deleted":
		if "4:comment_id" in change["logparams"]:
			link = link_formatter(create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"])))
		else:
			link = link_formatter(create_article_path(change["title"]))
		target_user = change["title"].split(':', 1)[1]
		if target_user != author:
			content = _("[{author}]({author_url}) deleted a [comment]({comment}) on {target}'s profile".format(author=author,author_url=author_url, comment=link, target=target_user))
		else:
			content = _("[{author}]({author_url}) deleted a [comment]({comment}) on their own profile".format(author=author, author_url=author_url, comment=link))
	elif action == "curseprofile/profile-edited":
		target_user = change["title"].split(':', 1)[1]
		link = link_formatter(create_article_path("UserProfile:{user}".format(user=target_user)))
		if target_user != author:
			content = _("[{author}]({author_url}) edited the {field} on [{target}]({target_url})'s profile. *({desc})*").format(author=author,
				                                                                author_url=author_url,
				                                                                target=target_user,
				                                                                target_url=link,
				                                                                field=profile_field_name(change["logparams"]['4:section'], False),
				                                                                desc=BeautifulSoup(change["parsedcomment"], "lxml").get_text())
		else:
			content = _("[{author}]({author_url}) edited the {field} on [their own]({target_url}) profile. *({desc})*").format(
				author=author,
				author_url=author_url,
				target_url=link,
				field=profile_field_name(change["logparams"]['4:section'], False),
				desc=BeautifulSoup(change["parsedcomment"], "lxml").get_text())
	elif action in ("rights/rights", "rights/autopromote"):

	elif action == "protect/protect":

	elif action == "protect/modify":

	elif action == "protect/unprotect":

	elif action == "delete/revision":

	elif action == "import/upload":

	elif action == "delete/restore":

	elif action == "delete/event":

	elif action == "import/interwiki":

	elif action == "abusefilter/modify":
	elif action == "abusefilter/create":

	elif action == "merge/merge":

	elif action == "newusers/autocreate":
	elif action == "newusers/create":
	elif action == "newusers/create2":
	elif action == "newusers/byemail":
	elif action == "newusers/newusers":
	elif action == "interwiki/iw_add":
	elif action == "interwiki/iw_edit":

	elif action == "interwiki/iw_delete":
		link = link_formatter(create_article_path("Special:Interwiki"))
	elif action == "contentmodel/change":

	elif action == "contentmodel/new":

	elif action == "sprite/sprite":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) edited the sprite for [{article}]({article_url})").format(author=author, author_url=author_url, article=change["title"], article_url=link)
	elif action == "sprite/sheet":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) created the sprite sheet for [{article}]({article_url})").format(author=author, author_url=author_url, article=change["title"], article_url=link)
	elif action == "sprite/slice":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) edited the slice for [{article}]({article_url})").format(author=author, author_url=author_url, article=change["title"], article_url=link)
	elif action == "cargo/createtable":

	elif action == "cargo/deletetable":

	elif action == "cargo/recreatetable":

	elif action == "cargo/replacetable":

	elif action == "managetags/create":

	elif action == "managetags/delete":

	elif action == "managetags/activate":

	elif action == "managetags/deactivate":
		link = link_formatter(create_article_path(change["title"]))
	elif action == "managewiki/settings":  # Miraheze's ManageWiki extension https://github.com/miraheze/ManageWiki

	elif action == "managewiki/delete":

	elif action == "managewiki/lock":

	elif action == "managewiki/namespaces":

	elif action == "managewiki/namespaces-delete":

	elif action == "managewiki/rights":

	elif action == "managewiki/undelete":

	elif action == "managewiki/unlock":

	elif action == "datadump/generate":
		content = _("[{author}]({author_url}) generated *{file}* dump{comment}").format(
			author=author, author_url=author_url, file=change["logparams"]["filename"],
			comment=parsed_comment
		)
	elif action == "datadump/delete":
		content = _("[{author}]({author_url}) deleted *{file}* dump{comment}").format(
			author=author, author_url=author_url, file=change["logparams"]["filename"],
			comment=parsed_comment
		)
	elif action == "pagetranslation/mark":
		link = create_article_path(change["title"])
		if "?" in link:
			link = link + "&oldid={}".format(change["logparams"]["revision"])
		else:
			link = link + "?oldid={}".format(change["logparams"]["revision"])
		link = link_formatter(link)
		content = _("[{author}]({author_url}) marked [{article}]({article_url}) for translation{comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/unmark":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) removed [{article}]({article_url}) from the translation system{comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/moveok":
		link = link_formatter(create_article_path(change["logparams"]["target"]))
		content = _("[{author}]({author_url}) completed moving translation pages from *{article}* to [{target}]({target_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], target=change["logparams"]["target"], target_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/movenok":
		link = link_formatter(create_article_path(change["title"]))
		target_url = link_formatter(create_article_path(change["logparams"]["target"]))
		content = _("[{author}]({author_url}) encountered a problem while moving [{article}]({article_url}) to [{target}]({target_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			target=change["logparams"]["target"], target_url=target_url,
			comment=parsed_comment
		)
	elif action == "pagetranslation/deletefok":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) completed deletion of translatable page [{article}]({article_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/deletefnok":
		link = link_formatter(create_article_path(change["title"]))
		target_url = link_formatter(create_article_path(change["logparams"]["target"]))
		content = _("[{author}]({author_url}) failed to delete [{article}]({article_url}) which belongs to translatable page [{target}]({target_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			target=change["logparams"]["target"], target_url=target_url,
			comment=parsed_comment
		)
	elif action == "pagetranslation/deletelok":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) completed deletion of translation page [{article}]({article_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/deletelnok":
		link = link_formatter(create_article_path(change["title"]))
		target_url = link_formatter(create_article_path(change["logparams"]["target"]))
		content = _("[{author}]({author_url}) failed to delete [{article}]({article_url}) which belongs to translation page [{target}]({target_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			target=change["logparams"]["target"], target_url=target_url,
			comment=parsed_comment
		)
	elif action == "pagetranslation/encourage":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) encouraged translation of [{article}]({article_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/discourage":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) discouraged translation of [{article}]({article_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "pagetranslation/prioritylanguages":
		link = link_formatter(create_article_path(change["title"]))
		if "languages" in change["logparams"]:
			languages = "`, `".join(change["logparams"]["languages"].split(","))
			if change["logparams"]["force"] == "on":
				content = _("[{author}]({author_url}) limited languages for [{article}]({article_url}) to `{languages}`{comment}").format(
					author=author, author_url=author_url,
					article=change["title"], article_url=link,
					languages=languages, comment=parsed_comment
				)
			else:
				content = _("[{author}]({author_url}) set the priority languages for [{article}]({article_url}) to `{languages}`{comment}").format(
					author=author, author_url=author_url,
					article=change["title"], article_url=link,
					languages=languages, comment=parsed_comment
				)
		else:
			content = _("[{author}]({author_url}) removed priority languages from [{article}]({article_url}){comment}").format(
				author=author, author_url=author_url,
				article=change["title"], article_url=link,
				comment=parsed_comment
			)
	elif action == "pagetranslation/associate":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) added translatable page [{article}]({article_url}) to aggregate group \"{group}\"{comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			group=change["logparams"]["aggregategroup"], comment=parsed_comment
		)
	elif action == "pagetranslation/dissociate":
		link = link_formatter(create_article_path(change["title"]))
		content = _("[{author}]({author_url}) removed translatable page [{article}]({article_url}) from aggregate group \"{group}\"{comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			group=change["logparams"]["aggregategroup"], comment=parsed_comment
		)
	elif action == "translationreview/message":
		link = create_article_path(change["title"])
		if "?" in link:
			link = link + "&oldid={}".format(change["logparams"]["revision"])
		else:
			link = link + "?oldid={}".format(change["logparams"]["revision"])
		link = link_formatter(link)
		content = _("[{author}]({author_url}) reviewed translation [{article}]({article_url}){comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			comment=parsed_comment
		)
	elif action == "translationreview/group":
		link = link_formatter(create_article_path(change["title"]))
		if "old-state" in change["logparams"]:
			content = _("[{author}]({author_url}) changed the state of `{language}` translations of [{article}]({article_url}) from `{old_state}` to `{new_state}`{comment}").format(
				author=author, author_url=author_url, language=change["logparams"]["language"],
				article=change["logparams"]["group-label"], article_url=link,
				old_state=change["logparams"]["old-state"], new_state=change["logparams"]["new-state"],
				comment=parsed_comment
			)
		else:
			content = _("[{author}]({author_url}) changed the state of `{language}` translations of [{article}]({article_url}) to `{new_state}`{comment}").format(
				author=author, author_url=author_url, language=change["logparams"]["language"],
				article=change["logparams"]["group-label"], article_url=link,
				new_state=change["logparams"]["new-state"], comment=parsed_comment
			)
	elif action == "pagelang/pagelang":
		link = link_formatter(create_article_path(change["title"]))
		old_lang = "`{}`".format(change["logparams"]["oldlanguage"])
		if change["logparams"]["oldlanguage"][-5:] == "[def]":
			old_lang = "`{}` {}".format(change["logparams"]["oldlanguage"][:-5], _("(default)"))
		new_lang = "`{}`".format(change["logparams"]["newlanguage"])
		if change["logparams"]["newlanguage"][-5:] == "[def]":
			new_lang = "`{}` {}".format(change["logparams"]["oldlanguage"][:-5], _("(default)"))
		content = _("[{author}]({author_url}) changed the language of [{article}]({article_url}) from {old_lang} to {new_lang}{comment}").format(
			author=author, author_url=author_url,
			article=change["title"], article_url=link,
			old_lang=old_lang, new_lang=new_lang, comment=parsed_comment
		)
	elif action == "renameuser/renameuser":
		link = link_formatter(create_article_path("User:"+change["logparams"]["newuser"]))
		edits = change["logparams"]["edits"]
		if edits > 0:
			content = ngettext("[{author}]({author_url}) renamed user *{old_name}* with {edits} edit to [{new_name}]({link}){comment}",
			                          "[{author}]({author_url}) renamed user *{old_name}* with {edits} edits to [{new_name}]({link}){comment}", edits).format(
				author=author, author_url=author_url, old_name=change["logparams"]["olduser"], edits=edits, new_name=change["logparams"]["newuser"], link=link, comment=parsed_comment
			)
		else:
			content = _("[{author}]({author_url}) renamed user *{old_name}* to [{new_name}]({link}){comment}").format(
				author=author, author_url=author_url, old_name=change["logparams"]["olduser"], new_name=change["logparams"]["newuser"], link=link, comment=parsed_comment
			)
	elif action == "suppressed":

	else:
		logger.warning("No entry for {event} with params: {params}".format(event=action, params=change))
		if not settings.get("support", None):
			return
		else:
			content = _(
				"Unknown event `{event}` by [{author}]({author_url}), report it on the [support server](<{support}>).").format(
				event=action, author=author, author_url=author_url, support=settings["support"])
			action = "unknown"
	send_to_discord(DiscordMessage("compact", action, settings["webhookURL"], content=content), meta=request_metadata)


def embed_formatter(action, change, parsed_comment, categories, recent_changes):
	embed = DiscordMessage("embed", action, settings["webhookURL"])
	request_metadata = DiscordMessageMetadata("POST", rev_id=change.get("revid", None), log_id=change.get("logid", None), page_id=change.get("pageid", None))
	if parsed_comment is None:
		parsed_comment = _("No description provided")
	if action != "suppressed":
		change["user"], author_url = format_user(change, recent_changes, action)
		embed.set_author(change["user"], author_url)
	if action in ("edit", "new"):  # edit or new page

	elif action in ("upload/overwrite", "upload/upload", "upload/revert"):  # sending files

	elif action == "delete/delete":

	elif action == "delete/delete_redir":

	elif action == "move/move":

	elif action == "move/move_redir":

	elif action == "protect/move_prot":

	elif action == "block/block":

	elif action == "block/reblock":

	elif action == "block/unblock":

	elif action == "curseprofile/comment-created":
		if settings["appearance"]["embed"]["show_edit_changes"]:
			parsed_comment = recent_changes.pull_comment(change["logparams"]["4:comment_id"])
		link = create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"]))
		target_user = change["title"].split(':', 1)[1]
		if target_user != change["user"]:
			embed["title"] = _("Left a comment on {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Left a comment on their own profile")
	elif action == "curseprofile/comment-replied":
		if settings["appearance"]["embed"]["show_edit_changes"]:
			parsed_comment = recent_changes.pull_comment(change["logparams"]["4:comment_id"])
		link = create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"]))
		target_user = change["title"].split(':', 1)[1]
		if target_user != change["user"]:
			embed["title"] = _("Replied to a comment on {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Replied to a comment on their own profile")
	elif action == "curseprofile/comment-edited":
		if settings["appearance"]["embed"]["show_edit_changes"]:
			parsed_comment = recent_changes.pull_comment(change["logparams"]["4:comment_id"])
		link = create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"]))
		target_user = change["title"].split(':', 1)[1]
		if target_user != change["user"]:
			embed["title"] = _("Edited a comment on {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Edited a comment on their own profile")
	elif action == "curseprofile/profile-edited":
		target_user = change["title"].split(':', 1)[1]
		link = create_article_path("UserProfile:{target}".format(target=target_user))
		if target_user != change["user"]:
			embed["title"] = _("Edited {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Edited their own profile")
		if not change["parsedcomment"]:  # If the field is empty
			parsed_comment = _("Cleared the {field} field").format(field=profile_field_name(change["logparams"]['4:section'], True))
		else:
			parsed_comment = _("{field} field changed to: {desc}").format(field=profile_field_name(change["logparams"]['4:section'], True), desc=BeautifulSoup(change["parsedcomment"], "lxml").get_text())
	elif action == "curseprofile/comment-purged":
		link = create_article_path(change["title"])
		target_user = change["title"].split(':', 1)[1]
		if target_user != change["user"]:
			embed["title"] = _("Purged a comment on {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Purged a comment on their own profile")
	elif action == "curseprofile/comment-deleted":
		if "4:comment_id" in change["logparams"]:
			link = create_article_path("Special:CommentPermalink/{commentid}".format(commentid=change["logparams"]["4:comment_id"]))
		else:
			link = create_article_path(change["title"])
		target_user = change["title"].split(':', 1)[1]
		if target_user != change["user"]:
			embed["title"] = _("Deleted a comment on {target}'s profile").format(target=target_user)
		else:
			embed["title"] = _("Deleted a comment on their own profile")
	elif action in ("rights/rights", "rights/autopromote"):

	elif action == "protect/protect":

	elif action == "protect/modify":

	elif action == "protect/unprotect":

	elif action == "delete/revision":

	elif action == "import/upload":

	elif action == "delete/restore":

	elif action == "delete/event":

	elif action == "import/interwiki":

	elif action == "abusefilter/modify":

	elif action == "abusefilter/create":

	elif action == "merge/merge":
	elif action == "newusers/autocreate":

	elif action == "newusers/create":

	elif action == "newusers/create2":

	elif action == "newusers/byemail":

	elif action == "newusers/newusers":

	elif action == "interwiki/iw_add":

	elif action == "interwiki/iw_edit":

	elif action == "interwiki/iw_delete":

	elif action == "contentmodel/change":

	elif action == "contentmodel/new":

	elif action == "sprite/sprite":
		link = create_article_path(change["title"])
		embed["title"] = _("Edited the sprite for {article}").format(article=change["title"])
	elif action == "sprite/sheet":
		link = create_article_path(change["title"])
		embed["title"] = _("Created the sprite sheet for {article}").format(article=change["title"])
	elif action == "sprite/slice":
		link = create_article_path(change["title"])
		embed["title"] = _("Edited the slice for {article}").format(article=change["title"])
	elif action == "cargo/createtable":

	elif action == "cargo/deletetable":

	elif action == "cargo/recreatetable":

	elif action == "cargo/replacetable":

	elif action == "managetags/create":

	elif action == "managetags/delete":

	elif action == "managetags/activate":

	elif action == "managetags/deactivate":

	elif action == "managewiki/settings":  # Miraheze's ManageWiki extension https://github.com/miraheze/ManageWiki

	elif action == "managewiki/delete":

	elif action == "managewiki/lock":

	elif action == "managewiki/namespaces":

	elif action == "managewiki/namespaces-delete":

	elif action == "managewiki/rights":

	elif action == "managewiki/undelete":

	elif action == "managewiki/unlock":

	elif action == "datadump/generate":
		embed["title"] = _("Generated {file} dump").format(file=change["logparams"]["filename"])
		link = create_article_path(change["title"])
	elif action == "datadump/delete":
		embed["title"] = _("Deleted {file} dump").format(file=change["logparams"]["filename"])
		link = create_article_path(change["title"])
	elif action == "pagetranslation/mark":
		link = create_article_path(change["title"])
		if "?" in link:
			link = link + "&oldid={}".format(change["logparams"]["revision"])
		else:
			link = link + "?oldid={}".format(change["logparams"]["revision"])
		embed["title"] = _("Marked \"{article}\" for translation").format(article=change["title"])
	elif action == "pagetranslation/unmark":
		link = create_article_path(change["title"])
		embed["title"] = _("Removed \"{article}\" from the translation system").format(article=change["title"])
	elif action == "pagetranslation/moveok":
		link = create_article_path(change["logparams"]["target"])
		embed["title"] = _("Completed moving translation pages from \"{article}\" to \"{target}\"").format(article=change["title"], target=change["logparams"]["target"])
	elif action == "pagetranslation/movenok":
		link = create_article_path(change["title"])
		embed["title"] = _("Encountered a problem while moving \"{article}\" to \"{target}\"").format(article=change["title"], target=change["logparams"]["target"])
	elif action == "pagetranslation/deletefok":
		link = create_article_path(change["title"])
		embed["title"] = _("Completed deletion of translatable page \"{article}\"").format(article=change["title"])
	elif action == "pagetranslation/deletefnok":
		link = create_article_path(change["title"])
		embed["title"] = _("Failed to delete \"{article}\" which belongs to translatable page \"{target}\"").format(article=change["title"], target=change["logparams"]["target"])
	elif action == "pagetranslation/deletelok":
		link = create_article_path(change["title"])
		embed["title"] = _("Completed deletion of translation page \"{article}\"").format(article=change["title"])
	elif action == "pagetranslation/deletelnok":
		link = create_article_path(change["title"])
		embed["title"] = _("Failed to delete \"{article}\" which belongs to translation page \"{target}\"").format(article=change["title"], target=change["logparams"]["target"])
	elif action == "pagetranslation/encourage":
		link = create_article_path(change["title"])
		embed["title"] = _("Encouraged translation of \"{article}\"").format(article=change["title"])
	elif action == "pagetranslation/discourage":
		link = create_article_path(change["title"])
		embed["title"] = _("Discouraged translation of \"{article}\"").format(article=change["title"])
	elif action == "pagetranslation/prioritylanguages":
		link = create_article_path(change["title"])
		if "languages" in change["logparams"]:
			languages = "`, `".join(change["logparams"]["languages"].split(","))
			if change["logparams"]["force"] == "on":
				embed["title"] = _("Limited languages for \"{article}\" to `{languages}`").format(article=change["title"], languages=languages)
			else:
				embed["title"] = _("Priority languages for \"{article}\" set to `{languages}`").format(article=change["title"], languages=languages)
		else:
			embed["title"] = _("Removed priority languages from \"{article}\"").format(article=change["title"])
	elif action == "pagetranslation/associate":
		link = create_article_path(change["title"])
		embed["title"] = _("Added translatable page \"{article}\" to aggregate group \"{group}\"").format(article=change["title"], group=change["logparams"]["aggregategroup"])
	elif action == "pagetranslation/dissociate":
		link = create_article_path(change["title"])
		embed["title"] = _("Removed translatable page \"{article}\" from aggregate group \"{group}\"").format(article=change["title"], group=change["logparams"]["aggregategroup"])
	elif action == "translationreview/message":
		link = create_article_path(change["title"])
		if "?" in link:
			link = link + "&oldid={}".format(change["logparams"]["revision"])
		else:
			link = link + "?oldid={}".format(change["logparams"]["revision"])
		embed["title"] = _("Reviewed translation \"{article}\"").format(article=change["title"])
	elif action == "translationreview/group":
		link = create_article_path(change["title"])
		embed["title"] = _("Changed the state of `{language}` translations of \"{article}\"").format(language=change["logparams"]["language"], article=change["title"])
		if "old-state" in change["logparams"]:
			embed.add_field(_("Old state"), change["logparams"]["old-state"], inline=True)
		embed.add_field(_("New state"), change["logparams"]["new-state"], inline=True)
	elif action == "pagelang/pagelang":
		link = create_article_path(change["title"])
		old_lang = "`{}`".format(change["logparams"]["oldlanguage"])
		if change["logparams"]["oldlanguage"][-5:] == "[def]":
			old_lang = "`{}` {}".format(change["logparams"]["oldlanguage"][:-5], _("(default)"))
		new_lang = "`{}`".format(change["logparams"]["newlanguage"])
		if change["logparams"]["newlanguage"][-5:] == "[def]":
			new_lang = "`{}` {}".format(change["logparams"]["oldlanguage"][:-5], _("(default)"))
		embed["title"] = _("Changed the language of \"{article}\"").format(article=change["title"])
		embed.add_field(_("Old language"), old_lang, inline=True)
		embed.add_field(_("New language"), new_lang, inline=True)
	elif action == "renameuser/renameuser":
		edits = change["logparams"]["edits"]
		if edits > 0:
			embed["title"] = ngettext("Renamed user \"{old_name}\" with {edits} edit to \"{new_name}\"", "Renamed user \"{old_name}\" with {edits} edits to \"{new_name}\"", edits).format(old_name=change["logparams"]["olduser"], edits=edits, new_name=change["logparams"]["newuser"])
		else:
			embed["title"] = _("Renamed user \"{old_name}\" to \"{new_name}\"").format(old_name=change["logparams"]["olduser"], new_name=change["logparams"]["newuser"])
		link = create_article_path("User:"+change["logparams"]["newuser"])
	elif action == "suppressed":

	else:
		logger.warning("No entry for {event} with params: {params}".format(event=action, params=change))
		link = create_article_path("Special:RecentChanges")
		embed["title"] = _("Unknown event `{event}`").format(event=action)
		embed.event_type = "unknown"
		if settings.get("support", None):
			change_params = "[```json\n{params}\n```]({support})".format(params=json.dumps(change, indent=2),
			                                                             support=settings["support"])
			if len(change_params) > 1000:
				embed.add_field(_("Report this on the support server"), settings["support"])
			else:
				embed.add_field(_("Report this on the support server"), change_params)
	embed["url"] = quote(link.replace(" ", "_"), "/:?=&")
	if parsed_comment is not None:
		embed["description"] = parsed_comment
	if settings["appearance"]["embed"]["show_footer"]:
		embed["timestamp"] = change["timestamp"]
	if "tags" in change and change["tags"]:
		tag_displayname = []
		for tag in change["tags"]:
			if tag in recent_changes.tags:
				if recent_changes.tags[tag] is None:
					continue  # Ignore hidden tags
				else:
					tag_displayname.append(recent_changes.tags[tag])
			else:
				tag_displayname.append(tag)
		embed.add_field(_("Tags"), ", ".join(tag_displayname))
	if len(embed["title"]) > 254:
		embed["title"] = embed["title"][0:253]+"…"
	logger.debug("Current params in edit action: {}".format(change))
	if categories is not None and not (len(categories["new"]) == 0 and len(categories["removed"]) == 0):
		new_cat = (_("**Added**: ") + ", ".join(list(categories["new"])[0:16]) + ("\n" if len(categories["new"])<=15 else _(" and {} more\n").format(len(categories["new"])-15))) if categories["new"] else ""
		del_cat = (_("**Removed**: ") + ", ".join(list(categories["removed"])[0:16]) + ("" if len(categories["removed"])<=15 else _(" and {} more").format(len(categories["removed"])-15))) if categories["removed"] else ""
		embed.add_field(_("Changed categories"), new_cat + del_cat)
	embed.finish_embed()
	send_to_discord(embed, meta=request_metadata)
