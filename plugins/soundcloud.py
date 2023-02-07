from __future__ import unicode_literals

import re
from util import hook, http


soundcloud_track_re = (
    r"soundcloud.com/([-_a-z0-9]+)/([-_a-z0-9/]+)",
    re.I,
)

BASE_URL = "https://soundcloud.com/"


@hook.regex(*soundcloud_track_re)
def soundcloud_track(match):
    url = BASE_URL + match.group(1) + "/" + match.group(2)
    d = http.get_html(url)

    # iso 8601 fmt expected, e.g. PT01H53M22S
    duration = d.find('.//meta[@itemprop="duration"]').get('content')
    duration = duration.replace("PT", "").replace("00H", "").lower().strip('0')

    # iso 8601 fmt expected, e.g. 2022-12-30T21:09:15Z
    published = d.find('.//time[@pubdate]').text[:10]

    title = d.find('.//a[@itemprop="url"]').text
    name = d.find('.//meta[@itemprop="name"]').get('content')
    plays = d.find('.//meta[@property="soundcloud:play_count"]').get('content')

    interactions = d.findall('.//meta[@itemprop="interactionCount"]')
    likes = 0
    for i in interactions:
        content = i.get("content", "")
        if "UserLikes" in content:
            likes = content.split(":")[1]

    out = (
        "\x02{title}\x02 by "
        "\x02{name}\x02 - "
        "length \x02{duration}\x02 - "
        "{likes}\u2191 - "
        "\x02{plays}\x02 plays - "
        "on \x02{published}\x02"
    )

    output = out.format(title=title, duration=duration, likes=likes,
                        plays=plays, name=name, published=published)

    return output + " - " + url
